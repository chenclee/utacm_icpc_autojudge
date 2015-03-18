import datetime
import pickle
import time
import threading
import sets


class Contest:
    verdicts = {'QU': 'In Queue',
                'CE': 'Compile Error',
                'AC': 'Accepted',
                'WA': 'Wrong Answer',
                'RE': 'Runtime Error',
                'TL': 'Time Limit Exceeded',
                'ML': 'Memory Limit Exceeded',
                'OL': 'Output Limit Exceeded'}

    def __init__(self, delay, duration, prob_ids, penalty, logger):
        """Initializes the contest.

        Parameter:
            delay - delay, in seconds, before starting the contest
            duration - duration, in seconds, of the contest
            problems - list of all prob_id's
        """
        assert delay >= 0
        assert duration >= 0
        self.init_time = int(time.time())
        self.start_time = self.init_time + delay
        self.end_time = self.start_time + duration
        self.prob_ids = prob_ids
        self.next_subm_id = 0
        self.submissions = {}
        self.scoreboard = []
        self.penalty = penalty
        self.frozen = False
        self.clarifs = []
        self.logger = logger

    def is_running(self):
        """Returns whether the contest is currently running."""
        return self.start_time <= time.time() < self.end_time

    def is_over(self):
        """Returns whether the contest is over."""
        return self.end_time <= time.time()

    def remaining_time(self):
        """Returns the remaining time of the contest in seconds."""
        now = time.time()
        if self.start_time - now > 0:
            return int(self.start_time - now)
        rem = int(self.end_time - now)
        return rem if rem > 0 else 0

    def extend(self, duration):
        """Extends the duration of the contest by duration.

        Parameters:
            duration - duration, in seconds, to extend the contest
        """
        self.end_time += duration

    def is_frozen(self):
        return self.frozen

    def freeze_scoreboard(self, freeze):
        """Freezes or unfreezes the scoreboard.

        Parameters:
            freeze - whether to freeze the scoreboard
        """
        if self.frozen == freeze:
            return
        self.frozen = freeze
        if freeze:
            self.scoreboard_copy = self.scoreboard
        else:
            self.scoreboard_copy = []

    def get_scoreboard(self, live=False):
        """Returns the current scoreboard or if the scoreboard is frozen,
        the scoreboard at the time of the freeze, unless live is set to
        True.

        Parameters:
            live - if this value is True, the scoreboard returned will always
                   be live, ignoring the frozen state of the scoreboard
        """
        return self.scoreboard if not self.frozen or live else self.scoreboard_copy

    def get_submissions(self, user_id):
        """Returns all submissions made by user_id sorted by submission time.

        Parameters:
            user_id - user id
        """
        return [self.submissions[subm_id] for subm_id in xrange(self.next_subm_id - 1, -1, -1)
                if self.submissions[subm_id]['user_id'] == user_id]

    def get_solved(self, user_id):
        """Returns whether each problem has been solved.

        Parameters:
            user_id - user id
        """
        solved = {prob_id: False for prob_id in self.prob_ids}
        for submission in self.get_submissions(user_id):
            if submission['result'] == 'AC':
                solved[submission['prob_id']] = True
        return solved

    def add_submission(self, user_id, prob_id, lang, submit_time, result='QU'):
        """Adds a submission result to the scoreboard.

        A submission is in the following format:
            {'user_id': ...,
             'prob_id': ...,
             'lang': ...,
             'submit_time': ...,
             'run_time': ...,
             'result': ...}

        Parameters:
            user_id - user id
            prob_id - problem id of submission
            submit_time - minute into contest of submission
            result - 'QU': In Queue
                     'CE': Compile Error

                     'AC': Accepted
                     'WA': Wrong Answer
                     'RE': Runtime Error
                     'TL': Time Limit Exceeded
                     'ML': Memory Limit Exceeded
                     'OL': Output Limit Exceeded
        """
        subm_id = self.next_subm_id
        self.next_subm_id += 1
        self.submissions[subm_id] = {'user_id': user_id,
                                     'prob_id': prob_id,
                                     'lang': lang,
                                     'submit_time': submit_time,
                                     'subm_id': subm_id,
                                     'run_time': 0.0,
                                     'result': result}
        self.logger.debug("submission: " + str(self.submissions[subm_id]))
        if result not in ('QU', 'CE'):
            self.update_scoreboard()
        return subm_id

    def change_submission(self, subm_id, result):
        """Changes the result of a submission.

        Parameters:
            subm_id - id of the submission to change.
            result - see #add_submission(...) for valid results
        """
        self.submissions[subm_id]['result'] = result
        self.update_scoreboard()

    def update_scoreboard(self):
        """Updates the scoreboard by recalculating each user's points and
        penalties.
        """
        points = {}
        for i in xrange(self.next_subm_id):
            s = self.submissions[i]
            u = s['user_id']
            if u not in points:
                points[u] = {'num_solved': 0, 'penalty': 0,
                             'solved': {pid: [-1, 0] for pid in self.prob_ids},
                             'accum': {pid: 0 for pid in self.prob_ids}}
            if points[u]['accum'][s['prob_id']] >= 0:
                points[u]['solved'][s['prob_id']][1] += 1
                if s['result'] == 'AC':
                    points[u]['solved'][s['prob_id']][0] = s['submit_time']
                    points[u]['num_solved'] += 1
                    points[u]['penalty'] += points[u]['accum'][s['prob_id']]
                    points[u]['penalty'] += s['submit_time']
                    points[u]['accum'][s['prob_id']] = -1
                elif s['result'] not in ('QU', 'CE'):
                    points[u]['accum'][s['prob_id']] += self.penalty

        # Make solved negative to sort by highest score, and fix negative after.
        self.scoreboard = sorted([(-points[user_id]['num_solved'],
                                   points[user_id]['penalty'],
                                   user_id,
                                   points[user_id]['solved'])
                                   for user_id in points])
        self.scoreboard = [(c, -a, b, d) for a, b, c, d in self.scoreboard]
        self.logger.debug("scoreboard: " + str(self.scoreboard))

    def reset_scoreboard(self):
        """Clears the entire scoreboard.

        Used by the judge for rejudging problems, in the event that
        there were incorrect specifications.
        """
        self.next_subm_id = 0
        self.submissions = {}
        self.scoreboard = []

    def get_clarifs(self, user_id):
        """Gets the clarifications/responses for a user.

        Parameters:
            user_id - id of the user to query
        """
        if user_id == -1:
            return tuple(self.clarifs)
        return tuple(c for c in self.clarifs if not c['private'] or c['user_id'] == user_id)

    def submit_clarif(self, user_id, prob_id, message):
        """Submits a clarification request.

        Parameters:
            user_id - id of the user submitting a request
            prob_id - id of the problem in question
            message - a short description of the clarification request
        """
        self.clarifs.append({'user_id': user_id, 'prob_id': prob_id,
                             'message': message, 'response': None,
                             'private': True})

    def respond_clarif(self, clarif_id, response, private=True):
        """Responds to a clarification request.

        Parameters:
            clarif_id - id of the clarif to respond to
            response - response to the clarification
            private - whether response should be private to user who submitted
                the request (default: True)
        """
        try:
            self.clarifs[clarif_id]['response'] = response
            self.clarifs[clarif_id]['private'] = private
            return True
        except:
            return False

    def create_global_clarif(self, prob_id, response):
        try:
            self.clarifs.append({'user_id': -1, 'prob_id': prob_id,
                             'message': 'Judge Clarification', 'response': response,
                             'private': False})
            return True;
        except:
            return False;
