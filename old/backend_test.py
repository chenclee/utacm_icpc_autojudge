import unittest
import os
import shutil

from backend import AutoJudger, Problem, Submission, Verdict


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
        submission0 = Submission('A', ('test-user',), 'Python 2.7', 'temp', 'print "INCORRECT"')
        submission1 = Submission('B', ('test-user2',), 'Python 2.7', 'blah.py', 'print "INCORRECT"')
        submission2 = Submission('A', ('test-user',), 'Python 2.7', 'a.py', 'print "CORRECT"')
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


    def test_judge_submission_java(self):
        shutil.rmtree('submissions/', ignore_errors=True)
        judger = AutoJudger(Problem('A'))
        submission0 = Submission('A', 'test-user', 'Java 6, 7', 'Main.java',
            'public class Main{public static void main(String[] args){System.out.println("5");}}')
        submission1 = Submission('A', 'test-user2', 'Java 6, 7', 'Main.java',
            'public class Main{public static void main(String[] args){System.out.println("5");}}')
        submission2 = Submission('A', 'test-user', 'Java 6, 7', 'Main.java',
            'import java.util.Scanner; public class Main{public static void main(String[] args){Scanner in=new Scanner(System.in);System.out.println(in.nextInt());}}')
        judger.judge(submission0)
        judger.judge(submission1)
        judger.judge(submission2)
        self.assertEqual(submission0.verdict, Verdict.wa)
        self.assertEqual(submission1.verdict, Verdict.wa)
        self.assertEqual(submission2.verdict, Verdict.ac)
        shutil.rmtree('submissions/')

    def test_judge_submission_python(self):
        shutil.rmtree('submissions/', ignore_errors=True)
        judger = AutoJudger(Problem('A'))
        submission0 = Submission('A', 'test-user', 'Python 2.7', 'temp', 'print "5"\n')
        submission1 = Submission('A', 'test-user2', 'Python 2.7', 'blah.py', 'print "5"\n')
        submission2 = Submission('A', 'test-user', 'Python 2.7', 'a.py', 'print raw_input()\n')
        judger.judge(submission0)
        judger.judge(submission1)
        judger.judge(submission2)
        self.assertEqual(submission0.verdict, Verdict.wa)
        self.assertEqual(submission1.verdict, Verdict.wa)
        self.assertEqual(submission2.verdict, Verdict.ac)
        shutil.rmtree('submissions/')

    def test_judge_submission_error_submit(self):
        shutil.rmtree('submissions/', ignore_errors=True)
        judger = AutoJudger(Problem('A'))
        submission0 = Submission('A', 'test-user', 'Python', 'temp',
                'i=0\nwhile True:\n  i+=1')
        judger.judge(submission0)
        self.assertEqual(submission0.verdict, Verdict.se)
        shutil.rmtree('submissions/')

    def test_judge_submission_error_timeout(self):
        shutil.rmtree('submissions/', ignore_errors=True)
        judger = AutoJudger(Problem('A'))
        submission0 = Submission('A', 'test-user', 'Python 2.7', 'temp',
                'i=0\nwhile True:\n  i+=1')
        judger.judge(submission0)
        self.assertEqual(submission0.verdict, Verdict.tl)
        shutil.rmtree('submissions/')

    def test_judge_submission_error_compile(self):
        shutil.rmtree('submissions/', ignore_errors=True)
        judger = AutoJudger(Problem('A'))
        submission0 = Submission('A', 'test-user', 'Java 6, 7', 'Temp.java',
                'i=0\nwhile True:\n  i+=1')
        judger.judge(submission0)
        self.assertEqual(submission0.verdict, Verdict.ce)
        shutil.rmtree('submissions/')

    def test_judge_submission_error_runtime(self):
        shutil.rmtree('submissions/', ignore_errors=True)
        judger = AutoJudger(Problem('A'))
        submission0 = Submission('A', 'test-user', 'Python 2.7', 'temp',
                'i=0\nwhile True:\n  i++')
        judger.judge(submission0)
        self.assertEqual(submission0.verdict, Verdict.re)
        shutil.rmtree('submissions/')

    def tearDown(self):
        shutil.rmtree('problems/', ignore_errors=True)
        shutil.rmtree('submissions/', ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
