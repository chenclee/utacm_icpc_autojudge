import logging
import time
import threading
import os
import uuid
import Queue


class Verdict(object):
    qu = 0 # In Queue
    ac = 1 # Accepted
    wa = 2 # Wrong Answer
    ce = 3 # Compile Error
    re = 4 # Runtime Error
    tl = 5 # Time Limit Exceeded
    ml = 6 # Memory Limit Exceeded
    ol = 7 # Output Limit Exceeded
    se = 8 # Submission Error
    rf = 9 # Restricted Function


lang_compile = {'GNU C++ 4': 'g++ -static -fno-optimize-sibling-calls -fno-strict-aliasing -DONLINE_JUDGE -lm -s -x c++ -Wl,--stack=268435456 -O2 -o prog_bin {filename}',
        'GNU C++11 4': 'g++ -static -fno-optimize-sibling-calls -fno-strict-aliasing -DONLINE_JUDGE -lm -s -x c++ -Wl,--stack=268435456 -O2 -std=c++11 -D__USE_MINGW_ANSI_STDIO=0 -o prog_bin {filename}',
        'GNU C 4': 'gcc -static -fno-optimize-sibling-calls -fno-strict-aliasing -DONLINE_JUDGE -fno-asm -lm -s -Wl,--stack=268435456 -O2 -o prog_bin {filename}',
        'Java 6, 7': 'javac -cp ".;*" {filename}',
        'Python 2.7': ';',
}
lang_run = {'GNU C++ 4': './prog_bin',
        'GNU C++11 4': './prog_bin',
        'GNU C 4': './prog_bin',
        'Java 6, 7': 'java -Xmx512M -Xss64M -DONLINE_JUDGE=true -Duser.language=en -Duser.region=US -Duser.variant=US -jar {filename}',
        'Python 2.7': 'python {filename}',
}


class Submission(object):
    path = 'submissions/'

    next_sid = 0
    @classmethod
    def get_next_sid(cls):
        sid = cls.next_sid
        cls.next_sid += 1
        return str(sid)

    def __init__(self, pid, uid, lang, filename, content):
        self.pid = pid
        self.sid = Submission.get_next_sid()
        self.uid = uid
        self.verdict = Verdict.qu
        self.time = time.time()
        self.filename = os.path.join(Submission.path, self.uid, self.pid, self.sid, filename)
        if not os.path.exists(os.path.dirname(self.filename)):
            os.makedirs(os.path.dirname(self.filename))
        with open(self.filename, 'w+') as out_file:
            out_file.write(content)

    def __str__(self):
        return 'pid=%s;sid=%s;uid=%s;time=%s;verdict=%s' % \
                (self.pid, self.sid, self.uid, self.time, self.verdict.__name__)


class Problem(object):
    path = 'problems/'
    cfg_filename = 'constraints.txt'
    statement_filename = 'statement.html'

    def __init__(self, pid):
        self.pid = pid
        with open(os.path.join(Problem.path, pid, Problem.cfg_filename), 'r') as in_file:
            self.config = eval(in_file.read().replace('\n', ''))
        with open(os.path.join(Problem.path, pid, Problem.statement_filename), 'r') as in_file:
            self.statement = in_file.read()

    def judge(self, submission):
        # TODO(chencjlee): actually implement judging
        submission.verdict = Verdict.ac


class Scoreboard(object):
    def __init__(self, problems):
        self.start_time = time.time()
        self.cache_lock = threading.Lock()
        self.cache = {}

    def new_submission(self, submission):
        logging.info('New submission: %s' % submission)
        judge_queue.put(submission)
        self.cache_lock.acquire()
        self.cache[submission.sid] = submission
        self.cache_lock.release()
