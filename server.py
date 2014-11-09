import json
import os
import uuid

from functools import wraps

from tornado import ioloop, web, auth, httpserver, gen, escape
from tornado.options import options, parse_command_line, define

from contest import Contest
from judge import Judge

define('admin_whitelist', default='chencjlee@gmail.com',
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
        return (cookie['email'], cookie['name'])


class AuthLoginHandler(BaseHandler, auth.GoogleMixin):
    @gen.coroutine
    def get(self):
        if self.get_argument('openid.mode', None):
            user = yield self.get_authenticated_user()
            self.set_secure_cookie('utacm_contest_user',
                                   escape.json_encode(user))
            self.redirect('/')
            return
        self.authenticate_redirect(ax_attrs=['name', 'email',
            'language', 'username'])


class AuthLogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie('utacm_contest_user')
        self.write("You are now logged out.")


class IndexHandler(BaseHandler):
    @web.authenticated
    def get(self):
        self.write('Welcome, %s' % self.get_current_user_id()[1])
        # Serve page
        # Make sure to send pre-contest page if pre-contest
        # should be asynchronous
        pass


class UpdatesHandler(BaseHandler):
    @web.authenticated
    def get(self):
        # Send updates in json form
        # Updates being: remaining time, scoreboard, clarifications
        # should be asynchronous
        pass


class PermitsHandler(BaseHandler):
    @web.authenticated
    def post(self):
        # Requests a new permit. Body should be just the prob_id
        # Return ttl of permit or -1 if max permits have been issued
        # should be asynchronous
        pass


class FilesHandler(BaseHandler):
    @web.authenticated
    def get(self, prob_id):
        # Sends the input file for the specified problem
        # verify valid prob_id
        # Check permit, return error if expired
        # should be asynchronous
        pass

    @web.authenticated
    def post(self, prob_id):
        # Requests a solution be graded
        # Body should contain: source code, output
        # verify valid prob_id
        # Check permit, return error if expired
        # Dispatch to judge, return True or False based on accepted or not
        # should be asynchronous
        pass


class AdminHandler(BaseHandler):
    @web.authenticated
    def get(self):
        if not self.is_admin():
            return

        rem = contest.remaining_time()
        webpage = '''<h1>======== DEBUG ========</h1><br>
        <b>Contest is currently running:</b> %s<br>
        <b>Remaining time</b>: %02d:%02d:%02d<br>
        <b>Scoreboard</b>:<br>
        %s<br>
        <b>Clarifications</b>:<br>
        %s<br>
        <h1>====== END DEBUG ======</h1><br>''' % (
            contest.is_running(),
            int(rem / 60 / 60),
            int(rem / 60 % 60),
            int(rem % 60),
            json.dumps(contest.get_scoreboard(), indent=4),
            json.dumps(contest.get_clarifs(-1), indent=4),
        )
        self.write(webpage)
        # TODO: move logic code out of console.py to here

    def is_admin(self):
        if self.get_current_user_id()[0] not in options.admin_whitelist:
            self.redirect('/')
            return False
        return True



if __name__ == '__main__':
    parse_command_line()

    print 'Loading contest config files...'
    contest_cfg_path = os.path.join(options.contest_dir, 'config.txt')
    with open(contest_cfg_path, 'r') as in_file:
        contest_cfg = eval(in_file.read())
        print 'Contest configuration:'
        print json.dumps(contest_cfg, indent=4)

    contest = Contest(options.delay, contest_cfg['duration'],
                      contest_cfg['prob_ids'], contest_cfg['penalty'])
    judge = Judge(contest, contest_cfg['prob_ids'], options.contest_dir)

    application = web.Application(
        [
            (r'/', IndexHandler),
            (r'/index', IndexHandler),
            (r'/admin/', AdminHandler),
            (r'/auth/login', AuthLoginHandler),
            (r'/auth/logout', AuthLogoutHandler),
            (r'/api/v1/updates', UpdatesHandler),
            (r'/api/v1/permits', PermitsHandler),
            (r'/api/v1/files/(.*)', FilesHandler),
        ],
        cookie_secret='TODO: generate a random cookie',
        login_url='/auth/login',
        template_path=os.path.join(os.path.dirname(__file__), 'templates'),
        static_path=os.path.join(os.path.dirname(__file__), 'static'),
        xsrf_cookies=True,
    )

    application.listen(options.port)
    ioloop.IOLoop.instance().start()
