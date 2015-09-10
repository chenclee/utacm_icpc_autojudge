import time
import re
import os
import pickle
import datetime
import threading
import Queue
import uuid
import sys
import shlex
import traceback

import subprocess32 as subprocess

from contest import Contest

class Judge:
    lang_compile = {'GNU C++ 4': ['g++', '-static', '-DONLINE_JUDGE',
                                  '-lm', '-s', '-x', 'c++', '-O2'],
                    'GNU C++11 4': ['g++', '-static', '-DONLINE_JUDGE',
                                    '-lm', '-s', '-x', 'c++', '-std=c++11', '-O2'],
                    'GNU C 4': ['gcc', '-static', '-fno-optimize-sibling-calls',
                                '-fno-strict-aliasing', '-DONLINE_JUDGE', '-fno-asm',
                                '-lm', '-s', '-O2'],
                    'Java 6, 7': ['javac', '-cp', '".;*"']}

    lang_run = {'GNU C++ 4': ['./a.out'],
                'GNU C++11 4': ['./a.out'],
                'GNU C 4': ['./a.out'],
                'Java 6, 7': ['java', '-Xmx512M', '-Xss64M', '-DONLINE_JUDGE=true'],
                'Python 2.7': ['python'],
                'Python 3.4': ['python3']
    }

    def __init__(self, contest, problems, contest_dir, num_judges, logger):
        self.contest = contest
        self.problems = problems
        self.contest_dir = contest_dir
        self.queue = Queue.Queue()
        self.in_queue = {}
        self.logger = logger

        self.subm_dir = os.path.join(contest_dir, 'submissions')
        self.log_path = os.path.join(self.subm_dir, 'log.txt')

        if num_judges < 1:
            num_judges = 1
        elif num_judges > 10:
            num_judges = 10
        self.judging = True
        for i in xrange(num_judges):
            threading.Thread(target=self.judge_func, args=("judge%d" % i,)).start()

    def judge_func(self, user):
        while self.judging:
            result = 'JE'
            elapsed = 0.0
            user_id = None
            try:
                subm_id, log = self.queue.get(timeout=1)
                self.logger.info("%s: judging submission %d (%s, %s, %s, %s)" %
                        (user, subm_id, log['prob_id'], log['source_name'], log['lang'], log['user_id']))
                self.logger.debug("%s: log=%s" % (user, str(log)))
                self.contest.change_submission(subm_id, result='CJ')
                user_id = log['user_id']
                for name in os.listdir(log['path']):
                    file_path = os.path.join(log['path'], name)
                    try:
                        if name.endswith('.class') or name == 'a.out' or name.endswith('.pyc'):
                            os.unlink(file_path)
                    except Exception, e:
                        self.logger.exception('could not remove binaries')
                error_log = None
                if log['lang'] in Judge.lang_compile:
                    compile_cmd = Judge.lang_compile[log['lang']] + [log['source_name']]
                    self.logger.debug("%s: %s" % (user, ' '.join(compile_cmd)))
                    compiler = subprocess.Popen('cd "%s"; %s' % (log['path'].replace('"', '\\"'), ' '.join(compile_cmd)), shell=True, stderr=subprocess.PIPE)
                    try:
                        stderr_data = compiler.communicate(timeout=60)[1]
                        if compiler.returncode != 0:
                            result = 'CE'
                            self.logger.debug("%s: compile returned non-zero exit status" % user)
                            error_log = stderr_data
                            with open(os.path.join(log['path'], 'compile_errors.txt'), 'w') as out_file:
                                out_file.write(stderr_data)
                            raise AssertionError()
                    except subprocess.TimeoutExpired:
                        compiler.kill()
                        compiler.communicate()
                        elapsed = 60
                        result = 'CE'
                        self.logger.debug("%s: compile took longer than 60 seconds" % user)
                        error_log = 'Exceeded max time allowed (60 seconds) for compiling.'
                        with open(os.path.join(log['path'], 'compile_errors.txt'), 'w') as out_file:
                            out_file.write("Exceeded max time allowed (60 seconds) for compiling.")
                        raise AssertionError()
                prob = self.problems[log['prob_id']]
                run_cmd = ['time', '--portability'] + Judge.lang_run[log['lang']]
                if 'Java' in log['lang']:
                    run_cmd.append(log['source_name'][:-5])
                elif 'Python' in log['lang']:
                    run_cmd.append(log['source_name'])
                docker_name = str(uuid.uuid4())
                docker_cmd = ['docker', 'run', '-i',
                        '--name="%s"' % (docker_name,),
                        '--rm=true',
                        '--net="none"',
                        '--cpu-shares=128',
                        '-m="%dm"' % (prob.mem_limit,), '--read-only',
                        '-v', '"%s":/judging_dir:ro' % (os.path.abspath(log['path']),), '-w', '/judging_dir',
                        '-u', user, 'chenclee/sandbox',
                        ' '.join(run_cmd)]
                self.logger.debug("%s: %s: " % (user, ' '.join(docker_cmd)))
                runner = subprocess.Popen(shlex.split(' '.join(docker_cmd)),
                        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                try:
                    ran_to_completion = [True]
                    def timeout_func():
                        self.logger.debug("%s: time limit exceeded; killing docker container" % (user,))
                        ran_to_completion[0] = False
                        try:
                            subprocess.call(['docker', 'rm', '-f', docker_name])
                        except:
                            pass
                    timer = threading.Timer(prob.time_limit * 4, timeout_func)
                    timer.start()
                    stdout_data, stderr_data = runner.communicate(input=prob.input_text)
                    timer.cancel()
                    ran_to_completion = ran_to_completion[0]

                    with open(os.path.join(log['path'], 'runtime_output.txt'), 'w') as out_file:
                        out_file.write(stdout_data)
                    with open(os.path.join(log['path'], 'runtime_errors.txt'), 'w') as out_file:
                        out_file.write(stderr_data)

                    if ran_to_completion:
                        self.logger.debug("%s: program ran to completion" % (user,))
                        stderr_lines = stderr_data.splitlines()
                        if runner.returncode != 0:
                            if 'read unix /var/run/docker.sock' in stderr_lines[-1]:
                                stderr_lines = stderr_lines[:-1]
                            result = 'RE' if stderr_lines[0].strip() != 'Command terminated by signal 9' else 'ML'
                            raise AssertionError()
                        time_matches = [re.search('(\d+\.\d{2})', s) for s in stderr_lines[-2:]]
                        elapsed = sum([float(time_match.group(0)) for time_match in time_matches])
                        if elapsed > prob.time_limit:
                            self.logger.debug("%s: user+sys time exceeds time limit" % (user,))
                            raise subprocess.TimeoutExpired(
                                    cmd=' '.join(docker_cmd),
                                    timeout=prob.time_limit,
                                    output=None)
                        actual = [line.strip() for line in stdout_data.splitlines() if line.strip() != '']
                        expected = [line.strip() for line in prob.output_text.splitlines() if line.strip() != '']
                        self.logger.debug("%s: actual=%s" % (user, str(actual[:10])))
                        self.logger.debug("%s: expected=%s" % (user, str(expected[:10])))
                        if actual == expected:
                            result = 'AC'
                        else:
                            result = 'WA'
                    else:
                        self.logger.debug("%s: program exceeded time limit and was terminated" % (user,))
                        raise subprocess.TimeoutExpired(
                                cmd=' '.join(docker_cmd),
                                timeout=prob.time_limit,
                                output=None)
                except subprocess.TimeoutExpired:
                    elapsed = self.problems[log['prob_id']].time_limit
                    result = 'TL'
                    raise AssertionError()
            except Queue.Empty:
                continue
            except AssertionError:
                pass
            except Exception as e:
                self.logger.error("%s: %s" % (user, traceback.format_exception(*sys.exc_info())))
                result = 'JE'
            self.logger.info("%s: result for submission %d is %s" % (user, subm_id, Contest.verdicts[result]))
            self.contest.change_submission(subm_id, result=result, run_time=elapsed, error_log=error_log)
            if user_id:
                self.in_queue[user_id] -= 1
            self.queue.task_done()

            for name in os.listdir(log['path']):
                file_path = os.path.join(log['path'], name)
                try:
                    if name.endswith('.class') or name == 'a.out' or name.endswith('.pyc'):
                        os.unlink(file_path)
                except Exception, e:
                    self.logger.exception('could not remove binaries')

        self.logger.info(user + " halted")

    def halt_judging(self):
        self.judging = False

    def enqueue_submission(self, user_id, prob_id, lang, source_name, source):
        """Adds submission to judging queue.

        Submission is added as: (subm_id, 
                                 {"submit_time": ...,
                                  "user_id": ...,
                                  "prob_id": ...,
                                  "lang": ...,
                                  "path": ...,
                                  "source_name": ...})

        Parameters:
            user_id - user who is submitting output
            prob_id - problem the user is submitting output for
            lang - language source is in
            source_name - name of the source code file
            source - source code

        Returns:
            tuple with first argument being if submission was successfully queued
            and second argument being error message if not successful
            
        """
        # add submission to judging queue
        if user_id not in self.in_queue:
            self.in_queue[user_id] = 0
        if lang not in Judge.lang_run:
            self.logger.warn("Invalid language for source code: '%s'" % lang)
            return (False, "Invalid language choice: '%s'" % (lang,))
        elif not re.match(r'^[0-9a-zA-Z-_\.+]+$', source_name):
            self.logger.warn("Invalid filename for source code: '%s'" % source_name)
            return (False, "Invalid filename for source code: '%s'" % (source_name,))
        elif self.in_queue[user_id] > 1:
            self.logger.warn("Too many concurrent submissions.")
            return (False, "Too many concurrent submissions. Please wait until your other"
                    " submissions are judged.")
        self.in_queue[user_id] += 1
        submit_time = (int(time.time()) - self.contest.start_time) / 60
        subm_id = self.contest.add_submission(user_id, prob_id, lang, submit_time)
        path = os.path.join(self.subm_dir, str(user_id), prob_id, str(subm_id))
        source_path = os.path.join(path, source_name)
        if not os.path.exists(os.path.dirname(source_path)):
            os.makedirs(os.path.dirname(source_path))
        os.chmod(os.path.dirname(source_path), 0777)
        with open(source_path, 'w') as out_file:
            out_file.write(source)
        with open(self.log_path, 'a') as out_file:
            log = {"submit_time": submit_time,
                   "user_id": user_id,
                   "prob_id": prob_id,
                   "lang": lang,
                   "path": path,
                   "source_name": source_name}
            out_file.write("%s\n" % (log.__repr__(),))
        self.queue.put((subm_id, log))
        return (True, "Success")

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
                    if log['user_id'] not in self.in_queue:
                        self.in_queue[log['user_id']] = 0
                    self.in_queue[log['user_id']] += 1
                    self.queue.put((subm_id, log))
                except Exception as e:
                    print "Unable to parse log line:", e
