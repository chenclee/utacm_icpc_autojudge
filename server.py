import json
import logging
import os
import uuid
import signal
import sys
import traceback

from tornado import ioloop, web, auth, httpserver, gen, escape, log
from tornado.options import options, parse_command_line, define

from problem import Problem
from contest import Contest
from judge import Judge
from data_uri import DataURI


define('redirect_url',
       help='Google OAuth2 Redirect URL', type=str)
define('client_id',
       help='Google OAuth2 Client ID', type=str)
define('client_secret',
       help='Google OAuth2 Client Secret', type=str)
define('admin_whitelist',
       help='emails of admins', type=str, multiple=True)
define('port', default=8000,
       help='start on the given port', type=int)
define('contest_dir', default='contest',
       help='path to the contest files', type=str)
define('delay', default=15*60,
       help='delay (in seconds) before starting the contest', type=int)
define('admin_only', default=False,
       help='only allow admins to view site', type=bool)


class BaseHandler(web.RequestHandler):
    def get_current_user(self):
        user_json = self.get_secure_cookie('utacm_contest_user', max_age_days=1)
        return escape.json_decode(user_json) if user_json else None

    def current_user_id(self):
        cookie = self.current_user
        return (cookie['email'], cookie['name'])

    def current_user_pretty(self):
        return "%s (%s)" % self.current_user_id()

    def is_admin(self):
        return self.current_user_id()[0] in options.admin_whitelist


class AuthLoginHandler(BaseHandler, auth.GoogleOAuth2Mixin):
    @gen.coroutine
    def get(self):
        if self.get_argument('code', False):
            user = yield self.get_authenticated_user(
                redirect_uri=self.settings['google_redirect_url'],
                code=self.get_argument('code'))
            if not user:
                self.clear_all_cookies()
                raise web.HTTPError(500, 'Google authentication failed')

            self.xsrf_token
            access_token = str(user['access_token'])
            http_client = self.get_auth_http_client()
            response = yield http_client.fetch('https://www.googleapis.com/oauth2/v1/userinfo?access_token='+access_token)
            if not response:
                self.clear_all_cookies()
                raise web.HTTPError(500, 'Google authentication failed')

            user = json.loads(response.body)
            if options.admin_only and user['email'] not in options.admin_whitelist:
                logger.warn("%s (%s) attempted to sign in (admin only mode)" % (user["name"], user["email"]))
                raise web.HTTPError(403, 'Contest is running in admin only mode.')
            self.set_secure_cookie('utacm_contest_user', escape.json_encode(user), expires_days=1)
            logger.info("%s (%s) signed in" % (user["name"], user["email"]))
            self.redirect('/')
            return
        elif self.get_secure_cookie('utacm_contest_user'):
            self.redirect('/')
            return
        else:
            yield self.authorize_redirect(
                redirect_uri=self.settings['google_redirect_url'],
                client_id=self.settings['google_oauth']['key'],
                scope=['profile', 'email'],
                response_type='code',
                extra_params={'approval_prompt': 'auto'})


class AuthLogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie('utacm_contest_user')
        self.write("You are now logged out.")


class IndexHandler(BaseHandler):
    @web.authenticated
    def get(self):
        if contest.is_running() or contest.is_over():
            self.render('contest.html', admin=self.is_admin())
        else:
            self.render('pre-contest.html', admin=self.is_admin())


class MetadataHandler(BaseHandler):
    @web.authenticated
    def get(self):
        if not contest.is_running() and not contest.is_over():
            raise web.HTTPError(503)
        data = {
            'langs': Judge.lang_run.keys(),
            'prob_ids': contest_cfg['prob_ids'],
            'prob_contents': {prob_id: problems[prob_id].content
                              for prob_id in contest_cfg['prob_ids']},
            'verdicts': Contest.verdicts,
            'solved': contest.get_solved(self.current_user_id())
        }
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(data))


class UpdatesHandler(BaseHandler):
    @web.authenticated
    def get(self):
        updates = {'remaining_time': contest.remaining_time()}
        if contest.is_running() or contest.is_over():
            updates['scoreboard'] = contest.get_scoreboard(live=self.is_admin())
            updates['solved'] = contest.get_solved(self.current_user_id())
            updates['submissions'] = contest.get_submissions(self.current_user_id(), is_admin=self.is_admin())
            updates['clarifications'] = contest.get_clarifs(self.current_user_id(), is_admin=self.is_admin())
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(updates))


class SubmitSolutionHandler(BaseHandler):
    @web.authenticated
    def post(self, prob_id):
        # Requests a solution be graded
        # Body should contain: source code, output
        # Verify valid prob_id
        # Check permit, return error if expired
        # Dispatch to judge, return True or False based on accepted or not
        if not contest.is_running():
            raise web.HTTPError(503)
        if prob_id not in contest_cfg['prob_ids']:
            raise web.HTTPError(404)

        user_id = self.current_user_id()

        try:
            lang = self.get_argument('lang')[:32]
            filename = self.get_argument('filename')[:32]
            source = DataURI(self.get_argument('sourceFile')).data
        except:
            raise web.HTTPError(400)

        logger.info('%s requests judgement for a submission (%s, %s, %s)' %
                (self.current_user_pretty(), filename, lang, prob_id))
        result, err = judge.enqueue_submission(user_id, prob_id, lang, filename, source)
        logger.info('Submission successfully added to judge queue' if result else
                'Failed to add to judge queue')
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps((result, err)))


class SubmitClarificationHandler(BaseHandler):
    @web.authenticated
    def post(self, prob_id):
        if not contest.is_running():
            raise web.HTTPError(503)
        if prob_id not in contest_cfg['prob_ids']:
            raise web.HTTPError(404)
        user_id = self.current_user_id()
        message = self.get_argument('content')

        logger.info('%s requests clarification for problem %s' %
                (self.current_user_pretty(), prob_id))
        logger.debug('Clarification: ' + message)

        contest.submit_clarif(user_id, prob_id, message)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(True))


class ErrorFileHandler(BaseHandler):
    @web.authenticated
    def get(self, value):
        user_id = self.current_user_id()

        try:
            subm_id = int(value)
        except:
            raise web.HTTPError(400)

        error_log = contest.get_error_log(user_id, subm_id, is_admin=self.is_admin())
        if not error_log:
            raise web.HTTPError(404)
        self.set_header('Content-Type', 'text/html')
        self.write('<pre>')
        self.write(str(error_log))
        self.write('</pre>')


class LogHandler(BaseHandler):
    @web.authenticated
    def get(self, value):
        if not self.is_admin():
            raise web.HTTPError(404)
        self.set_header('Content-Type', 'text/html')
        self.write("<pre>")
        try:
            server_log_path = os.path.join(options.contest_dir, "server_log.txt")
            with open(server_log_path, 'r') as in_file:
                lines = [line.decode('utf-8') for line in in_file.readlines()]
                lines = [line for line in lines if all([v in line for v in value.split('/')])]
                self.write(''.join(lines))
        except:
            logger.error("unable to read log: %s" % (traceback.format_exception(*sys.exc_info()),))
            self.write("unable to read log")
        self.write("</pre>")


class AdminHandler(BaseHandler):
    @web.authenticated
    def get(self, value):
        if not self.is_admin():
            raise web.HTTPError(404)

        if value != 'updates':
            raise web.HTTPError(400)

        updates = {'frozen': contest.is_frozen(),
                   'whitelist': options.admin_whitelist,
                   'clarifs': contest.get_clarifs(-1)}
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(updates))

    @web.authenticated
    def post(self, put_type):
        if not self.is_admin():
            raise web.HTTPError(404)
        if put_type == 'rejudge':
            self.rejudge()
        elif put_type == 'clear':
            self.clear_cache()
        elif put_type == 'frozen':
            self.change_state()
        elif put_type == 'whitelist':
            self.add_to_whitelist()
        elif put_type == 'add_time':
            self.add_time()
        elif put_type == 'clarifications':
            self.respond_to_clarification()
        elif put_type == 'clarification':
            self.post_global_clarification()
        elif put_type == 'override':
            self.override_result()
        else:
            raise web.HTTPError(400)

    def rejudge(self):
        self.clear_cache()
        judge.rejudge_all()
        self.write(json.dumps(True))

    def clear_cache(self):
        for prob in problems.values():
            prob.reload_files()

    def change_state(self):
        new_state = ''
        try:
            new_state = self.get_argument('state')
        except Exception:
            raise web.HTTPError(400)
        if new_state == 'unfreeze':
            contest.freeze_scoreboard(False)
        else:
            contest.freeze_scoreboard(True)
        self.write(json.dumps(True))

    def override_result(self):
        try:
            subm_id = int(self.get_argument('subm_id'))
            result = self.get_argument('result')
            if result in Contest.verdicts:
                contest.change_submission(subm_id, result)
            self.write(json.dumps(True))
        except:
            raise web.HTTPError(400)

    def add_to_whitelist(self):
        newAdmin = ''
        try:
            new_admin = self.get_argument('newAdmin')
        except Exception:
            raise web.HTTPError(400)
        if new_admin not in options.admin_whitelist:
            options.admin_whitelist.append(new_admin)
        self.write(json.dumps(True))

    def add_time(self):
        num_min = 0;
        try:
            num_min = int(self.get_argument('numMin'))
        except Exception:
            raise web.HTTPError(400)

        contest.extend(num_min * 60)
        self.write(json.dumps(True))

    def respond_to_clarification(self):
        option = 0;
        clarif_id = ''
        try:
            option = int(self.get_argument('respNum'))
            clarif_id = int(self.get_argument('clarifNum'))
        except Exception:
            raise web.HTTPError(400)

        if option == 0:
            contest.respond_clarif(clarif_id, 'Reread the problem statement.')
            self.write(json.dumps(True))
        elif option == 1:
            contest.respond_clarif(clarif_id, 'Come talk to the administrators.')
            self.write(json.dumps(True))
        elif option == 2:
            resp_string = ''
            try:
                resp_string = self.get_argument('response')
            except Exception:
                raise web.HTTPError(400)
            contest.respond_clarif(clarif_id, resp_string, False)
            self.write(json.dumps(True))
        else:
            raise web.HTTPError(400)

    def post_global_clarification(self):
        prob_id = 0;
        resp_string = ''
        try:
            prob_id = self.get_argument('probId')
            resp_string = self.get_argument('response')
        except Exception:
            raise web.HTTPError(400)
        contest.create_global_clarif(prob_id, resp_string)
        self.write(json.dumps(True))


def init_loggers():
    access_log_path = os.path.join(options.contest_dir, "access_log.txt")
    handler_access = logging.FileHandler(access_log_path)
    handler_access.setFormatter(log.LogFormatter())
    logging.getLogger('tornado.access').addHandler(handler_access)

    server_log_path = os.path.join(options.contest_dir, "server_log.txt")
    handler_server = logging.FileHandler(server_log_path)
    handler_server.setFormatter(log.LogFormatter())
    logger.addHandler(handler_server)
    logger.setLevel(logging.DEBUG)

    logger.info("Starting up server")


if __name__ == '__main__':
    parse_command_line()
    logger = logging.getLogger(__name__)
    init_loggers()

    logger.info("Loading contest configuration")
    with open(os.path.join(options.contest_dir, 'config.txt'), 'r') as in_file:
        contest_cfg = eval(in_file.read())
        
        seconds = contest_cfg['duration'] % 60
        minutes = contest_cfg['duration'] / 60 % 60
        hours = contest_cfg['duration'] / 60 / 60 % 60

        logger.debug("Duration: %02d:%02d:%02d" % (hours, minutes, seconds))
        logger.debug("Problems: " + str(contest_cfg['prob_ids']))
        logger.debug("Penalty: %d points / wrong submission" % contest_cfg['penalty'])

    problems = {prob_id: Problem(prob_id, options.contest_dir, logger)
                        for prob_id in contest_cfg['prob_ids']}
    contest = Contest(options.delay, contest_cfg['duration'],
                      contest_cfg['prob_ids'], contest_cfg['penalty'], logger)
    judge = Judge(contest, problems, options.contest_dir, logger)

    application = web.Application(
        [
            (r'/', IndexHandler),
            (r'/index.html', IndexHandler),
            (r'/auth/login', AuthLoginHandler),
            (r'/auth/logout', AuthLogoutHandler),
            (r'/api/v1/admin/(.*)', AdminHandler),
            (r'/api/v1/log/(.*)', LogHandler),
            (r'/api/v1/metadata', MetadataHandler),
            (r'/api/v1/updates', UpdatesHandler),
            (r'/api/v1/submit/(.*)/solution', SubmitSolutionHandler),
            (r'/api/v1/submit/(.*)/clarification', SubmitClarificationHandler),
            (r'/api/v1/errors/(.*)', ErrorFileHandler),
        ],
        cookie_secret=str(uuid.uuid4()),
        login_url='/auth/login',
        template_path=os.path.join(os.path.dirname(__file__), 'templates'),
        static_path=os.path.join(os.path.dirname(__file__), 'static'),
        xsrf_cookies=True,
        debug=False,
        google_redirect_url=options.redirect_url,
        google_oauth={'key': options.client_id, 'secret': options.client_secret},
    )

    application.listen(
        port=options.port,
        max_buffer_size=40*1024,
    )

    signal.signal(signal.SIGUSR1, lambda x, y: judge.halt_judging())

    logger.info("Setup complete, starting IOLoop")
    try:
        ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        logger.info("Server halted by ^C, shutting down judger")
    except Exception as e:
        logger.critical("Server crashed: %s" % e.message)
    finally:
        judge.halt_judging()
