import time
import re
import os
import pickle
import datetime
import threading
import Queue

from random import choice

class Judge:
    lang_compile = {'GNU C++ 4': ['g++', '-static', '-fno-optimize-sibling-calls',
                                  '-fno-strict-aliasing', '-DONLINE_JUDGE', '-lm',
                                  '-s', '-x', 'c++', '-Wl', '--stack=268435456',
                                  '-O2', '-o', 'prog_bin'],
                    'GNU C++11 4': ['g++', '--std=c++11', '-O2', '-o', 'prog_bin'],
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

    def __init__(self, contest, problems, contest_dir, logger):
        self.contest = contest
        self.problems = problems
        self.contest_dir = contest_dir
        self.queue = Queue.Queue()
        self.logger = logger

        self.subm_dir = os.path.join(contest_dir, 'submissions')
        self.log_path = os.path.join(self.subm_dir, 'log.txt')

        self.judger = threading.Thread(target=self.judge_next)
        self.judging = True
        self.judger.start()

    def judge_next(self):
        while self.judging:
            try:
                subm_id, log = self.queue.get(timeout=1)
                self.logger.info("Judging submission %d: %s, %s" %
                        (subm_id, log['user_id'], log['prob_id']))
                self.logger.debug("log: " + str(log))

                result = choice(['CE', 'AC', 'WA', 'RE', 'TL', 'ML', 'OL'])
                self.logger.info("Result: %s" % (result,))
                self.contest.change_submission(subm_id, result)
                self.queue.task_done()
            except Queue.Empty:
                pass
        self.logger.info("Judging has been halted")

    def halt_judging(self):
        self.judging = False

    def enqueue_submission(self, user_id, prob_id, lang, source_name, source):
        """Adds submission to judging queue.

        Submission is added as: (subm_id, 
                                 {"submit_time"  : ...,
                                  "user_id"    : ...,
                                  "prob_id"    : ...,
                                  "lang"       : ...,
                                  "source_path": ...})

        Parameters:
            user_id - user who is submitting output
            prob_id - problem the user is submitting output for
            lang - language source is in
            source_name - name of the source code file
            source - source code

        return - true if output was correct and false otherwise
        """
        # add submission to judging queue
        if lang not in Judge.lang_run:
            self.logger.warn("Invalid language for source code: '%s'" % lang)
            return False
        elif re.search(r'[^\w\.]', source_name):
            self.logger.warn("Invalid filename for source code: '%s'" % source_name)
            return False
        submit_time = (int(time.time()) - self.contest.start_time) / 60
        subm_id = self.contest.add_submission(user_id, prob_id, lang, submit_time)
        source_path = os.path.join(self.subm_dir, str(user_id), prob_id, str(subm_id), source_name)
        if not os.path.exists(os.path.dirname(source_path)):
            os.makedirs(os.path.dirname(source_path))
        with open(source_path, 'w') as out_file:
            out_file.write(source)
        with open(self.log_path, 'a') as out_file:
            log = {"submit_time": submit_time,
                   "user_id": user_id,
                   "prob_id": prob_id,
                   "lang": lang,
                   "source_path": source_path}
            out_file.write("%s\n" % (log.__repr__(),))
        self.queue.put((subm_id, log))
        return True

    def rejudge_all(self):
        """Regrade all submissions"""
        while True:
            try:
                item = self.queue.get_nowait()
                self.queue.task_done()
            except Queue.Empty:
                break
        self.queue.join()
        self.contest.reset_scoreboard()
        with open(self.log_path, 'r') as in_file:
            for line in in_file:
                try:
                    log = eval(line)
                    subm_id = self.contest.add_submission(
                            log['user_id'], log['prob_id'], log['lang'], log['submit_time'])
                    self.queue.put((subm_id, log))
                except Exception as e:
                    print "Unable to parse log line:", e
