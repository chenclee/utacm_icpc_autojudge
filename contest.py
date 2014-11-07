import time
import threading

class Contest:
    def __init__(self, delay, duration, prob_ids):
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
        self.frozen = False

    def is_running(self):
        """Returns whether the contest is currently running."""
        return self.start_time <= time.time() < self.end_time

    def remaining_time(self):
        """Returns the remaining time of the contest in seconds."""
        return int(self.end_time - time.time())

    def extend(self, duration):
        """Extends the duration of the contest by duration.

        Parameters:
            duration - duration, in seconds, to extend the contest
        """
        self.end_time += duration

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

    def submit_run(self, user_id, prob_id, submit_time, run_success):
        self.submitted_runs.append((user_id, prob_id, submit_time, run_success))

    def nullify_prob(self, prob_id):
        pass

    def clarifs(self):
        pass

    def submit_clarif(self, message):
        pass

    def respond_clarif(self, clarif_id, response):
        pass
