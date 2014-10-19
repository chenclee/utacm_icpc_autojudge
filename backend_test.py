import unittest

from backend import Scoreboard, Problem, Submission, Verdict


class TestBackend(unittest.TestCase):

    def setUp(self):
        pass

    def test_read_problem(self):
        prob = Problem('A')
        self.assertEqual(prob.config['time_limit'], 2)
        self.assertEqual(prob.config['memory_limit'], '256MB')


if __name__ == '__main__':
    unittest.main()
