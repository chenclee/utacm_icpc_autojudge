import json
import logging
import os
import uuid
import signal
import sys

from tornado import ioloop, web, auth, httpserver, gen, escape
from tornado.options import options, parse_command_line, define

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


class BaseHandler(web.RequestHandler):
    def get_current_user(self):
        user_json = self.get_secure_cookie('utacm_contest_user')
        if not user_json:
            return None
        return escape.json_decode(user_json)

    def get_current_user_id(self):
        cookie = self.get_current_user()
        return (cookie['email'], cookie['name']) if cookie else 'n/a'

    def is_admin(self):
        return self.get_current_user_id()[0] in options.admin_whitelist


class AuthLoginHandler(BaseHandler, auth.GoogleOAuth2Mixin):
    @gen.coroutine
    def get(self):
        if self.get_current_user():
            self.redirect('/')
            return

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
            self.set_secure_cookie('utacm_contest_user', escape.json_encode(user))
            logging.info(self.get_current_user_id() + " just logged in.")
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
        try:
            logging.info(self.get_current_user_id() + " just logged out.")
        except:
            pass
        self.clear_cookie('utacm_contest_user')
        self.write("You are now logged out.")


class IndexHandler(BaseHandler):
    @web.authenticated
    def get(self):
        # Serve page
        # Make sure to send pre-contest page if pre-contest
        # should be asynchronous
        try:
            logging.info(self.get_current_user_id() + " requested the webpage.")
        except:
            pass
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
            'prob_ids': contest_cfg['prob_ids'],
            'prob_contents': problem_contents,
            'remaining_permit_counts': judge.get_remaining_permit_counts(self.get_current_user_id()),
            'solved': judge.get_solved_problems(self.get_current_user_id()),
            'problems_time_to_solve': judge.get_problems_time_to_solve()
        }
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(data))


class UpdatesHandler(BaseHandler):
    @web.authenticated
    def get(self):
        # Send updates in json form
        # Updates being: remaining time, scoreboard, clarifications
        updates = {
            'remaining_time': contest.remaining_time(),
        }
        if contest.is_running() or contest.is_over():
            updates['scoreboard'] = contest.get_scoreboard()
            updates['clarifications'] = contest.get_clarifs(self.get_current_user_id())

        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(updates))


class PermitsHandler(BaseHandler):
    @web.authenticated
    def post(self):
        # Requests a new permit. Body should be just the prob_id
        # Return ttl of permit if max permits have been issued
        # Raises a 403 error if out of permits
        # should be asynchronous
        if not contest.is_running():
            raise web.HTTPError(503)
        user_id = self.get_current_user_id()
        prob_id = self.get_argument('content')
        create = json.loads(self.get_argument('create'))

        try:
            logging.info("%s requested a %spermit for prob %s" % (user_id, "new " if create else "", prob_id))
        except:
            pass

        if prob_id not in contest_cfg['prob_ids']:
            raise web.HTTPError(400)
        permit = judge.get_expiring_permit(user_id, prob_id, create)
        if permit is None and create:
            try:
                logging.info("%s's permit request rejected. Max requested already." % (user_id,))
            except:
                pass
            raise web.HTTPError(403)
        elif permit is None and not create:
            try:
                logging.info("%s requested permit history. No permits issued." % (user_id,))
            except:
                pass
            permit = None
        else:
            try:
                if create:
                    logging.info("%s issued permit %s." % (user_id, permit))
                else:
                    logging.info("%s was previously issued permit %s." % (user_id, permit))
            except:
                pass

        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(permit))


class InputFilesHandler(BaseHandler):
    @web.authenticated
    def get(self, prob_id):
        # Sends the input file for the specified problem
        # verify valid prob_id
        # Check permit, return error if expired
        if not contest.is_running():
            raise web.HTTPError(503)
        if prob_id not in contest_cfg['prob_ids']:
            raise web.HTTPError(404)
        user_id = self.get_current_user_id()
        text = judge.get_input_text(user_id, prob_id)
        if text is None:
            raise web.HTTPError(409)
        self.set_header('Content-Type', 'application/octet-stream')
        self.write(text)


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
        user_id = self.get_current_user_id()
        try:
            output = DataURI(self.get_argument('outputFile')).data
        except:
            raise web.HTTPError(400)
        try:
            source_code = DataURI(self.get_argument('sourceFile')).data
        except:
            raise web.HTTPError(400)
        result = judge.judge_submission(user_id, prob_id, source_code, output)
        if result is None:
            raise web.HTTPError(409)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result))


class SubmitClarificationHandler(BaseHandler):
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
        user_id = self.get_current_user_id()
        message = self.get_argument('content')
        contest.submit_clarif(user_id, prob_id, message)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(True))


class LogHandler(BaseHandler):
    @web.authenticated
    def get(self, value):
        if not self.is_admin():
            raise web.HTTPError(404)
        elif value != 'permits':
            raise web.HTTPError(400)

        self.set_header('Content-Type', 'application/json')
        if value == 'permits':
            self.write(json.dumps(judge.save_data()))



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
        else:
            raise web.HTTPError(400)

    def rejudge(self):
        prob_id = -1
        try:
            prob_id = self.get_argument('probId')
        except Exception:
            raise web.HTTPError(400)
        judge.rejudge_problem(prob_id)
        self.write(json.dumps(True))

    def clear_cache(self):
        problem_contents = {prob_id: get_problem_content(prob_id)
                            for prob_id in contest_cfg['prob_ids']}

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


def get_problem_content(prob_id):
    content_path = os.path.join(options.contest_dir,
                                'problems',
                                prob_id,
                                'content.html')
    with open(content_path, 'r') as in_file:
        return in_file.read()


if __name__ == '__main__':
    parse_command_line()

    contest_cfg_path = os.path.join(options.contest_dir, 'config.txt')
    with open(contest_cfg_path, 'r') as in_file:
        contest_cfg = eval(in_file.read())

    problem_contents = {prob_id: get_problem_content(prob_id)
                        for prob_id in contest_cfg['prob_ids']}

    contest = Contest(options.delay, contest_cfg['duration'],
                      contest_cfg['prob_ids'], contest_cfg['penalty'])
    judge = Judge(contest, contest_cfg['prob_ids'], options.contest_dir)

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
            (r'/api/v1/permits', PermitsHandler),
            (r'/api/v1/files/(.*)/input.txt', InputFilesHandler),
            (r'/api/v1/submit/(.*)/solution', SubmitSolutionHandler),
            (r'/api/v1/submit/(.*)/clarification', SubmitClarificationHandler),
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
        max_buffer_size=128*1024,
    )
    
    def save_data(a, b):
        judge.save_data()
        sys.exit(1)
    
    signal.signal(signal.SIGINT, save_data)
    
    ioloop.IOLoop.instance().start()
