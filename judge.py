#!/usr/bin/python

import logging
import tornado.auth
import tornado.escape
import tornado.ioloop
import tornado.web
import time
import threading
import os
import uuid
import Queue

from tornado.concurrent import Future
from tornado import gen
from tornado.options import define, options, parse_command_line

from backend import Scoreboard, Problem, Submission, Verdict


define('port', default=8000, help='start on the given port', type=int)
define('debug', default=False, help='run in debug mode')


scoreboard = Scoreboard([])
judge_queue = Queue.Queue()


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        user_json = self.get_secure_cookie('utacm_contest_user')
        if not user_json:
            return None
        return tornado.escape.json_decode(user_json)

    def get_current_uid(self):
        cookie = self.get_current_user()
        return (cookie['id'], cookie['name'])


class MainHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render('index.html')


class SubmitCodeHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        pass


class SubmitClarificationHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        pass


class ViewScoreboardHandler(BaseHandler):
    @tornado.web.authenticated
    @gen.coroutine
    def post(self):
        pass

    def on_connection_close(self):
        pass


class ViewSubmissionsHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        # TODO: Fill submissiontest with real data
        #
        # Format of submissionTest:
        # [
        #   [ submission 1 ],
        #   [ submission 2 ],
        #   ...
        # ]
        # where the format of a submission is:
        # [
        #   Position in array (1 for first submission, 2 for second, ...),
        #   Problem name,
        #   Submission ID,
        #   Submission time,
        #   Verdict,
        #   Link to the file (this currently won't work, we'll need to hash it out)
        # ]
        submissionTest = []
        for i, submission in enumerate(scoreboard.get_by_uid(self.get_current_uid())):
            submissionTest.append([i + 1, submission.pid, submission.sid,
                               int((submission.time - scoreboard.start_time) / 60),
                               submission.verdict, ""])
        self.render('submissions.html', submissions=submissionTest)


class AuthLoginHandler(BaseHandler, tornado.auth.GoogleMixin):
    @gen.coroutine
    def get(self):
        if self.get_argument('openid.mode', None):
            user = yield self.get_authenticated_user()
            user['id'] = str(uuid.uuid4())
            self.set_secure_cookie('utacm_contest_user',
                                   tornado.escape.json_encode(user))
            self.redirect('/')
            return
        self.authenticate_redirect(ax_attrs=['name'])


class AuthLogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie('utacm_contest_user')
        self.write("You are now logged out")


def main():
    parse_command_line()
    app = tornado.web.Application(
            [
                (r'/', MainHandler),
                (r'/auth/login', AuthLoginHandler),
                (r'/auth/logout', AuthLogoutHandler),
                (r'/a/submit/code', SubmitCodeHandler),
                (r'/a/submit/clarification', SubmitClarificationHandler),
                (r'/a/view/scoreboard', ViewScoreboardHandler),
                (r'/a/view/submissions', ViewSubmissionsHandler),
            ],
            cookie_secret='TODO(chencjlee): Generate a random value',
            login_url='/auth/login',
            template_path='templates',
            static_path='static',
            xsrf_cookies=True,
            debug=options.debug,
    )
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
