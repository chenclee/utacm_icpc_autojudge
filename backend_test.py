import unittest
import os
import shutil

from backend import Scoreboard, Problem, Submission, Verdict


class TestBackend(unittest.TestCase):

    def setUp(self):
        shutil.rmtree('problems/', ignore_errors=True)
        shutil.rmtree('submissions/', ignore_errors=True)
        os.makedirs(os.path.dirname('problems/A/'))
        with open('problems/A/constraints.txt', 'w+') as out_file:
            out_file.write('{"time_limit": 2, "memory_limit": "256MB"}')
        with open('problems/A/statement.html', 'w+') as out_file:
            out_file.write('<h1>Problem A</h1>')
        with open('problems/A/in-00.txt', 'w+') as out_file:
            out_file.write('5\n')
        with open('problems/A/out-00.txt', 'w+') as out_file:
            out_file.write('5\n')
        with open('problems/A/in-01.txt', 'w+') as out_file:
            out_file.write('10\n')
        with open('problems/A/out-01.txt', 'w+') as out_file:
            out_file.write('10\n')
        pass

    def test_read_problem(self):
        prob = Problem('A')
        self.assertEqual(prob.config['time_limit'], 2)
        self.assertEqual(prob.config['memory_limit'], '256MB')
        self.assertEqual(prob.statement, '<h1>Problem A</h1>')

    def test_create_submission(self):
        shutil.rmtree('submissions/', ignore_errors=True)
        submission0 = Submission('A', 'test-user', 'Python 2.7', 'temp', 'print "INCORRECT"')
        submission1 = Submission('B', 'test-user2', 'Python 2.7', 'blah.py', 'print "INCORRECT"')
        submission2 = Submission('A', 'test-user', 'Python 2.7', 'a.py', 'print "CORRECT"')
        self.assertTrue(os.path.exists('submissions/test-user/A/0/temp'))
        with open('submissions/test-user/A/0/temp', 'r') as in_file:
            self.assertEqual(in_file.read(), 'print "INCORRECT"')
        self.assertTrue(os.path.exists('submissions/test-user2/B/1/blah.py'))
        with open('submissions/test-user2/B/1/blah.py', 'r') as in_file:
            self.assertEqual(in_file.read(), 'print "INCORRECT"')
        self.assertTrue(os.path.exists('submissions/test-user/A/2/a.py'))
        with open('submissions/test-user/A/2/a.py', 'r') as in_file:
            self.assertEqual(in_file.read(), 'print "CORRECT"')
        shutil.rmtree('submissions/')

    def test_judge_submission_python(self):
        shutil.rmtree('submissions/', ignore_errors=True)
        prob = Problem('A')
        submission0 = Submission('A', 'test-user', 'Python 2.7', 'temp', 'print "5"\n')
        submission1 = Submission('A', 'test-user2', 'Python 2.7', 'blah.py', 'print "5"\n')
        submission2 = Submission('A', 'test-user', 'Python 2.7', 'a.py', 'print raw_input()\n')
        prob.judge(submission0)
        prob.judge(submission1)
        prob.judge(submission2)
        self.assertEqual(submission0.verdict, Verdict.wa)
        self.assertEqual(submission1.verdict, Verdict.wa)
        self.assertEqual(submission2.verdict, Verdict.ac)
        shutil.rmtree('submissions/')

    def tearDown(self):
        shutil.rmtree('problems/', ignore_errors=True)
        shutil.rmtree('submissions/', ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
