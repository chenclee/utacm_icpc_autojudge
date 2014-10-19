#!/usr/bin/python

import logging
import tornado.auth
import tornado.escape
import tornado.ioloop
import tornado.web
import time
import threading
import os
import sys
import uuid

from tornado.concurrent import Future
from tornado import gen
from tornado.options import define, options, parse_command_line

from backend import Scoreboard, Problem, Submission, Verdict


define('port', default=8000, help='start on the given port', type=int)
define('debug', default=False, help='run in debug mode')

with open('problems/problems.txt', 'r') as cfg_file:
    problems = [Problem(*t) for t in eval(cfg_file.read().strip())]
scoreboard = Scoreboard(problems, time.time(), time.time() + 60 * 60 * 2, time.time() + 60 * 60 * 3)


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
        uploaded = self.request.files['source'][0]
        filename = uploaded['filename']
        content = uploaded['body']
        submission = Submission(self.get_arguments('pid')[0], self.get_current_uid(),
                'Python 2.7', filename, content)
        scoreboard.new_submission(submission)
        self.redirect('/a/view/submissions')


class SubmitClarificationHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        pass


class ViewScoreboardHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        # Format of problem set:
        # [
        #   'Problem 1',
        #   'Problem 2',
        #   ...
        # ]
        problemSet = [problem.name for problem in problems]

        # Format of scoreboard:
        # [
        #   Current Place,
        #   Name,
        #   [
        #     time to complete problem 1/attempts,
        #     time to complete problem 2/attempts,
        #     ...
        #   ]
        # ]
        board = scoreboard.get()
        self.render('scoreboard.html', problemSet=problemSet, scoreboard=board)


class ViewSubmissionsHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
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
        #   Programming Language Used,
        #   Verdict,
        #   Link to the file (this currently won't work, we'll need to hash it out)
        # ]
        submissionTest = []
        for i, submission in enumerate(scoreboard.get_by_uid(self.get_current_uid())):
            submissionTest.append([i + 1, submission.pid, submission.sid,
                               int((submission.time - scoreboard.start_time) / 60),
                               submission.lang, Verdict.pretty_string(submission.verdict), ""])
        self.render('submissions.html', submissions=submissionTest)

class ViewProblemsHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        # Format:
        # [
        #   [
        #     short, 1 word id of problem,
        #     Name of problem
        #   ],
        #   [ ... ], ...
        # ]
        problemList = [problem.short() for problem in problems]

        # Format:
        # [
        #   [
        #     short, 1 word id of problem,
        #     Name of problem,
        #     Description of problem
        #   ],
        #   [ ... ], ...
        # ]
        problemSet = [problem.detailed() for problem in problems]
        self.render('problems.html', problemList=problemList, problemSet=problemSet)

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
                (r'/a/view/problems', ViewProblemsHandler),
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
    try:
        main()
    except KeyboardInterrupt:
        print "Terminating contest..."
