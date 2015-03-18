import time
import re
import os
import pickle
import datetime
import threading
import Queue
import uuid

import subprocess32

from contest import Contest

class Judge:
    lang_compile = {'GNU C++ 4': ['g++', '-static', '-DONLINE_JUDGE',
                                  '-lm', '-s', '-x', 'c++', '-O2',
                                  '-o', 'prog_bin'],
                    'GNU C++11 4': ['g++', '-static', '-DONLINE_JUDGE',
                                    '-lm', '-s', '-x', 'c++', '-std=c++11', '-O2',
                                    '-o', 'prog_bin'],
                    'GNU C 4': ['gcc', '-static', '-fno-optimize-sibling-calls',
                                '-fno-strict-aliasing', '-DONLINE_JUDGE', '-fno-asm',
                                '-lm', '-s', '-O2',
                                '-o', 'prog_bin'],
                    'Java 6, 7': ['javac', '-cp', '".;*"']}

    lang_run = {'GNU C++ 4': ['./prog_bin'],
                'GNU C++11 4': ['./prog_bin'],
                'GNU C 4': ['./prog_bin'],
                'Java 6, 7': ['java', '-Xmx512M', '-Xss64M', '-DONLINE_JUDGE=true'],
                'Python 2.7': ['python'],
                'Python 3.4': ['python3']
    }

    def __init__(self, contest, problems, contest_dir, logger):
        self.contest = contest
        self.problems = problems
        self.contest_dir = contest_dir
        self.queue = Queue.Queue()
        self.logger = logger

        self.subm_dir = os.path.join(contest_dir, 'submissions')
        self.log_path = os.path.join(self.subm_dir, 'log.txt')

        self.judger = threading.Thread(target=self.judge_func)
        self.judging = True
        self.judger.start()

    def judge_func(self):
        while self.judging:
            result = 'QU'
            elapsed = 0.0
            try:
                subm_id, log = self.queue.get(timeout=1)
                self.logger.info("Judging submission %d: %s, %s" %
                        (subm_id, log['user_id'], log['prob_id']))
                self.logger.debug("log: " + str(log))

                if log['lang'] in Judge.lang_compile:
                    compile_cmd = Judge.lang_compile[log['lang']] + [log['source_name']]
                    docker_cmd = ['docker', 'run', '-v',
                            '"%s":/judging_dir' % (os.path.abspath(log['path']),),
                            '-w', '/judging_dir', 'chenclee/sandbox',
                            '/bin/sh', '-c', "'%s'" % ' '.join(compile_cmd)]
                    self.logger.debug("docker_cmd: " + ' '.join(docker_cmd))
                    compiler = subprocess32.Popen(' '.join(docker_cmd), shell=True, stderr=subprocess32.PIPE)
                    try:
                        stderr_data = compiler.communicate(timeout=2)[1]
                        if compiler.returncode != 0:
                            result = 'CE'
                            with open(os.path.join(log['path'], 'compile_errors.txt'), 'w') as out_file:
                                out_file.write(stderr_data)
                            raise AssertionError()
                    except subprocess32.TimeoutExpired:
                        compiler.kill()
                        compiler.communicate()
                        result = 'CE'
                        with open(os.path.join(log['path'], 'errors.txt'), 'w') as out_file:
                            out_file.write("Compile Time Exceeded (2 seconds)\n")
                        raise AssertionError()

                prob = self.problems[log['prob_id']]
                run_cmd = ['time', '--portability'] + Judge.lang_run[log['lang']]
                if 'Java' in log['lang']:
                    run_cmd.append(log['source_name'][:-5])
                elif 'Python' in log['lang']:
                    run_cmd.append(log['source_name'])
                docker_cmd = ['docker', 'run', '-i',
                        '-m="%dm"' % (prob.mem_limit,),
                        '-v', '"%s":/judging_dir' % (os.path.abspath(log['path']),),
                        '-w', '/judging_dir', 'chenclee/sandbox',
                        '/bin/sh', '-c', "'%s'" % ' '.join(run_cmd)]
                self.logger.debug("docker_cmd: " + ' '.join(docker_cmd))
                runner = subprocess32.Popen(' '.join(docker_cmd), shell=True,
                        stdin=subprocess32.PIPE, stdout=subprocess32.PIPE, stderr=subprocess32.PIPE)
                finished = False
                try:
                    stdout_data, stderr_data = runner.communicate(
                            input=prob.input_text(), timeout=(prob.time_limit * 4))
                    regex = re.compile("(\d+\.\d{2})")
                    self.logger.debug(stderr_data.splitlines()[-2:])
                    if runner.returncode != 0:
                        result = 'RE' if stderr_data.splitlines()[0].strip() != 'Command terminated by signal 9' else 'ML'
                        with open(os.path.join(log['path'], 'runtime_errors.txt'), 'w') as out_file:
                            out_file.write(stderr_data)
                        raise AssertionError()
                    time_matches = [regex.search(s) for s in stderr_data.splitlines()[-2:]]
                    elapsed = sum([float(time_match.group(0)) for time_match in time_matches])
                    if elapsed > prob.time_limit:
                        finished = True
                        raise subprocess32.TimeoutExpired(
                                cmd=' '.join(docker_cmd),
                                timeout=prob.time_limit,
                                output=None)
                    # TODO: check stdout to correct
                    with open(os.path.join(log['path'], 'output.txt'), 'w') as out_file:
                        out_file.write(stdout_data)
                    actual = [line.strip() for line in stdout_data.splitlines() if line.strip() != '']
                    expected = [line.strip() for line in prob.output_text().splitlines() if line.strip() != '']
                    self.logger.debug("actual: " + str(actual[:10]))
                    self.logger.debug("expected: " + str(expected[:10]))
                    if actual == expected:
                        result = 'AC'
                    else:
                        result = 'WA'
                except subprocess32.TimeoutExpired:
                    if not finished:
                        runner.kill()
                        runner.communicate()
                    elapsed = self.problems[log['prob_id']].time_limit
                    result = 'TL'
                    raise AssertionError()
            except Queue.Empty:
                continue
            except AssertionError:
                pass
            except Exception as e:
                self.logger.error("Unable to judge: " + e.message)
                result = 'JE'
            # result = choice(['CE', 'AC', 'WA', 'RE', 'TL', 'ML'])
            self.logger.info("Result: %s" % (Contest.verdicts[result],))
            self.contest.change_submission(subm_id, result=result, run_time=elapsed)
            self.queue.task_done()
        self.logger.info("Judging has been halted")

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
        path = os.path.join(self.subm_dir, str(user_id), prob_id, str(subm_id))
        source_path = os.path.join(path, source_name)
        if not os.path.exists(os.path.dirname(source_path)):
            os.makedirs(os.path.dirname(source_path))
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
