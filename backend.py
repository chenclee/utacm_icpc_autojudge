import logging
import time
import threading
import os
import uuid
import subprocess
import Queue

import util


class Verdict(object):
    qu = 0 # In Queue
    ac = 1 # Accepted
    wa = 2 # Wrong Answer
    ce = 3 # Compile Error
    re = 4 # Runtime Error
    tl = 5 # Time Limit Exceeded
    ml = 6 # Memory Limit Exceeded
    se = 7 # Submission Error
    rf = 8 # Restricted Function
    cj = 9 # Can't Be Judged


lang_compile = {'GNU C++ 4': ['g++', '-static', '-fno-optimize-sibling-calls',
                              '-fno-strict-aliasing', '-DONLINE_JUDGE', '-lm',
                              '-s', '-x', 'c++', '-Wl', '--stack=268435456',
                              '-O2', '-o', 'prog_bin'],
                'GNU C++11 4': ['g++', '-static', '-fno-optimize-sibling-calls',
                                '-fno-strict-aliasing', '-DONLINE_JUDGE', '-lm',
                                '-s', '-x', 'c++', '-Wl', '--stack=268435456',
                                '-O2', '-std=c++11', '-D__USE_MINGW_ANSI_STDIO=0',
                                '-o', 'prog_bin'],
                'GNU C 4': ['gcc', '-static', '-fno-optimize-sibling-calls',
                            '-fno-strict-aliasing', '-DONLINE_JUDGE', '-fno-asm',
                            '-lm', '-s', '-Wl', '--stack=268435456', '-O2',
                            '-o', 'prog_bin'],
                'Java 6, 7': ['javac', '-cp', '".;*"']}

lang_run = {'GNU C++ 4': ['./prog_bin'],
            'GNU C++11 4': ['./prog_bin'],
            'GNU C 4': ['./prog_bin'],
            'Java 6, 7': ['java', '-Xmx512M', '-Xss64M', '-DONLINE_JUDGE=true'],
            'Python 2.7': ['python']
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
        self.lang = lang
        self.verdict = Verdict.qu
        self.time = time.time()
        self.filepath = os.path.join(Submission.path, self.uid[0], self.pid, self.sid)
        self.filename = filename
        if not os.path.exists(self.filepath):
            os.makedirs(self.filepath)
        with open(os.path.join(self.filepath, self.filename), 'w+') as out_file:
            out_file.write(content)

    def __str__(self):
        return 'pid=%s;sid=%s;uid=%s;time=%s;verdict=%s' % \
                (self.pid, self.sid, self.uid[0], self.time, self.verdict)

# os.path.dirname

class Problem(object):
    path = 'problems/'
    cfg_filename = 'constraints.txt'
    statement_filename = 'statement.html'
    input_filename = 'in-%02d.txt'
    output_filename = 'out-%02d.txt'

    def __init__(self, pid):
        self.pid = pid
        with open(os.path.join(Problem.path, pid, Problem.cfg_filename), 'r') as in_file:
            self.config = eval(in_file.read().replace('\n', ''))
        with open(os.path.join(Problem.path, pid, Problem.statement_filename), 'r') as in_file:
            self.statement = in_file.read()
        self.test_filenames = []
        for i in xrange(100):
            input_filename = os.path.join(Problem.path, pid, Problem.input_filename % i)
            output_filename = os.path.join(Problem.path, pid, Problem.output_filename % i)
            if not os.path.exists(input_filename):
                break
            self.test_filenames.append((os.path.abspath(input_filename),
                                        os.path.abspath(output_filename)))


    def judge(self, submission):
        # TODO(chencjlee): test C++, C++11, C
        if submission.lang not in lang_run:
            submission.verdict = Verdict.se
        else:
            orig_path = os.getcwd()
            try:
                os.chdir(submission.filepath)
                compiled = True
                if submission.lang in lang_compile:
                    compile_cmd = lang_compile[submission.lang][:]
                    compile_cmd.append(submission.filename)
                    if util.TimeoutCommand().run(compile_cmd, subprocess.PIPE, 2)[0] != 0:
                        submission.verdict = Verdict.ce
                        compiled = False
                if compiled:
                    run_cmd = lang_run[submission.lang][:]
                    if run_cmd[0] != './prog_bin':
                        run_cmd.append(submission.filename.replace('.java', ''))
                    for input_filename, output_filename in self.test_filenames:
                        with open(input_filename, 'r') as input_file, \
                                open(output_filename, 'r') as output_file:
                            return_code, actual_output = util.TimeoutCommand().run(
                                run_cmd, input_file, self.config['time_limit'])
                            if return_code == -15:
                                submission.verdict = max(submission.verdict, Verdict.tl)
                            elif return_code != 0:
                                submission.verdict = max(submission.verdict, Verdict.re)
                            else:
                                expected_output = output_file.read()
                                if actual_output.strip() != expected_output.strip():
                                    submission.verdict = max(submission.verdict, Verdict.wa)
                                else:
                                    submission.verdict = max(submission.verdict, Verdict.ac)
            except Exception as e:
                logging.warning('Exception while judging: %s' % submission)
                submission.verdict = Verdict.cj
            finally:
                os.chdir(orig_path)


class Scoreboard(object):
    def __init__(self, problems):
        self.start_time = time.time()
        self.cache_lock = threading.Lock()
        self.cache = {}

    def new_submission(self, submission):
        logging.info('New submission: %s' % submission)
        self.cache_lock.acquire()
        if submission.uid not in self.cache:
            self.cache[submission.uid] = []
        self.cache[submission.uid].append(submission)
        self.cache_lock.release()

    def get_by_uid(self, uid):
        submissions = []
        self.cache_lock.acquire()
        if uid in self.cache:
            submissions = self.cache[uid][::-1]
        self.cache_lock.release()
        return submissions
