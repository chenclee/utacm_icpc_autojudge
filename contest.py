import time
import threading


class Contest:
    def __init__(self, delay, duration, prob_ids, penalty):
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
        self.submitted_runs = []
        self.cached_scoreboard = {}
        self.penalty = penalty
        self.frozen = False
        self.clarifs = []

    def is_running(self):
        """Returns whether the contest is currently running."""
        return self.start_time <= time.time() < self.end_time

    def remaining_time(self):
        """Returns the remaining time of the contest in seconds."""
        rem = int(self.end_time - time.time())
        return rem if rem > 0 else 0

    def extend(self, duration):
        """Extends the duration of the contest by duration.

        Parameters:
            duration - duration, in seconds, to extend the contest
        """
        self.end_time += duration

    def recompute_scoreboard(self):
        """Recomputes the scoreboard."""
        scoreboard = {}
        for entry in self.submitted_runs:
            if entry[0] not in scoreboard:
                scoreboard[entry[0]] = {
                    'penalty': 0,
                    'attempts': {prob_id: 0 for prob_id in self.prob_ids},
                    'solved': {prob_id: None for prob_id in self.prob_ids},
                    'score': 0
                }
            if scoreboard[entry[0]]['solved'][entry[1]] is not None:
                continue
            if entry[3]:
                time_solved = int((entry[2] - self.start_time) / 60.0)
                scoreboard[entry[0]]['solved'][entry[1]] = time_solved
                scoreboard[entry[0]]['score'] += 1
                scoreboard[entry[0]]['penalty'] += (
                    self.penalty * scoreboard[entry[0]]['attempts'][entry[1]]
                    + time_solved)
            scoreboard[entry[0]]['attempts'][entry[1]] += 1

        entries = []
        for user_id in scoreboard:
            sort_key = (-scoreboard[user_id]['solved'],
                        scoreboard[user_id]['penalty'])
            stats = []
            for prob_id in self.prob_ids:
                time_to_solve = int((scoreboard[user_id]['solved'][prob_id]
                                    - self.start_time) / 60)
                p1 = '-' if not correct else time_to_solve
                p2 = scoreboard[user_id]['attempts'][prob_id]
                stats.append("%s/%s" % (p1, p2))
            entries.append((sort_key, user_id[1], tuple(stats)))
        entries.sort()
        self.cached_scoreboard = tuple(entries)

    def freeze_scoreboard(self, freeze):
        """Freezes or unfreezes the scoreboard.

        Parameters:
            freeze - whether to freeze the scoreboard
        """
        self.frozen = freeze
        if not self.frozen:
            self.recompute_scoreboard()

    def get_scoreboard(self):
        """Returns the current scoreboard or if the scoreboard is frozen,
        the scoreboard at the time of the freeze.
        """
        return self.cached_scoreboard

    def submit_result(self, user_id, prob_id, submit_time, result):
        """Submits the results for a user submission to the scoreboard.

        Parameters:
            user_id - user id
            prob_id - problem id of submission
            submit_time - time of submission (use time.time())
            result - whether the submission was bueno
        """
        self.submitted_runs.append(
            (user_id, prob_id, submit_time, result))
        if not self.frozen:
            self.recompute_scoreboard()

    def nullify_prob(self, prob_id):
        """Deletes ALL of the results for a given prob_id.

        Used by the judge for regrading a problem, in the event that
        there was incorrect judging.

        Parameters:
            prob_id - id of the problem, whose submissions to delete
        """
        self.submitted_runs = (
            [run for run in self.submitted_runs if run[1] != prob_id])

    def get_clarifs(self, user_id):
        """Gets the clarifications/responses for a user.

        Parameters:
            user_id - id of the user to query
        """
        if user_id == -1:
            return tuple(self.clarifs)
        return tuple(c for c in self.clarifs if c[0] == -1 or c[0] == user_id)

    def submit_clarif(self, user_id, prob_id, message):
        """Submits a clarification request.

        Parameters:
            user_id - id of the user submitting a request
            prob_id - id of the problem in question
            message - a short description of the clarification request
        """
        self.clarifs.append((user_id, prob_id, message, None))

    def respond_clarif(self, clarif_id, response, private=True):
        """Responds to a clarification request.

        Parameters:
            clarif_id - id of the clarif to respond to
            response - response to the clarification
            private - whether response should be private to user who submitted
                the request (default: True)
        """
        try:
            if private:
                self.clarifs[clarif_id] = (
                    self.clarifs[clarif_id][:3] + (response,))
            else:
                self.clarifs[clarif_id] = (
                    (-1,) + self.clarifs[clarif_id][1:3] + (response,))
            return True
        except:
            return False

    def get_submissions(self):
        return self.submitted_runs
