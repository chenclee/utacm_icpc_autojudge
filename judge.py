import time
import os


class Judge:

    def __init__(self, contest, prob_ids, contest_dir):
        """Read in config files for problem set

        contest - pointer to contest state obj
        permits - dict mapping users to problems to permits issued
        prob_cfgs - dict mapping problems to problem configurations
        submitted_runs - ???

        Parameters:
            contest  - pointer to contest object
            prob_ids - prob_ids
            contest_dir - path to contest files directory
        """
        self.contest = contest
        self.permits = {}
        self.contest_dir = contest_dir
        self.prob_cfgs = (
            {prob_id: self.load_cfg(prob_id) for prob_id in prob_ids})
        self.submitted_runs = {}

    def load_cfg(self, prob_id):
        """Read configuration file for a problem statement

        Parameter:
            prob_id - problem id to load configuration for

        return - dictionary of configuration parameters
        """
        path = '%s/problems/%s/config.txt' % (self.contest_dir, prob_id)
        with open(path, 'r') as in_file:
            return eval(in_file.read())

    def get_expiring_permit(self, user_id, prob_id):
        """Return a unique id and keep a record of its expiration date

        Parameters:
            user_id - unique user id
            prob_id - problem statement id

        Return - returns ttl or None if the max number
                 of permits for the user and problem has been reached.
        """
        if user_id not in self.permits:
            self.permits[user_id] = {prob_id: [] for prob_id in self.prob_cfgs}

        now = time.time()
        if len(self.permits[user_id][prob_id]) > 0:
            last_permit = self.permits[user_id][prob_id][-1]

            if last_permit['correct']:
                return None

            ttl = last_permit['expiration'] - now
            if ttl > 0 and last_permit['correct'] is None:
                return int(ttl)

        if (len(self.permits[user_id][prob_id])
                == self.prob_cfgs[prob_id]['max_attempts']):
            return None

        # if another attempt is valid, generate uuid and store data
        permit_num = len(self.permits[user_id][prob_id])
        self.permits[user_id][prob_id].append({
            'expiration': now + self.prob_cfgs[prob_id]['time_allowed'],
            'input_file': self.prob_cfgs[prob_id]['inputs'][permit_num],
            'output_file': self.prob_cfgs[prob_id]['outputs'][permit_num],
            'correct': None
        })
        return int(self.prob_cfgs[prob_id]['time_allowed'])

    def valid_permit(self, user_id, prob_id):
        """Test whether a permit is valid
        (eg exists and has not expired)

        Parameter:
            user_id - owner of the permit
            prob_id - problem the permit is for

        return - true if permit is valid and false otherwise
        """
        now = time.time()
        if (user_id in self.permits
                and prob_id in self.permits[user_id]
                and len(self.permits[user_id][prob_id]) > 0):
            return (now < self.permits[user_id][prob_id][-1]['expiration']
                    and self.permits[user_id][prob_id][-1]['correct'] is None)
        return False

    def get_input_text(self, user_id, prob_id):
        """Return input file data for user to run program on

        Parameter:
            user_id - user requesting the input file
            prob_id - problem the user is request input for

        return - test data for user to run their program on
        """
        if not self.valid_permit(user_id, prob_id):
            return None

        input_file = '%s/problems/%s/%s' % (
            self.contest_dir, prob_id,
            self.permits[user_id][prob_id][-1]['input_file'])
        with open(input_file, 'r') as in_file:
            return in_file.read()

    def judge_submission(self, user_id, prob_id, source, output):
        """Test output sent from contestant

        Parameters:
            user_id - user who is submitting output
            prob_id - problem the user is submitting output for
            source - source code
            output - output to test against correct output

        return - true if output was correct and false otherwise
        """
        if not self.valid_permit(user_id, prob_id):
            return None
        storage_string = '%s/submissions/%s/%s/%s' % (
            self.contest_dir, prob_id, user_id,
            self.permits[user_id][prob_id][-1]['output_file'])
        if not os.path.exists(os.path.dirname(storage_string)):
            os.makedirs(os.path.dirname(storage_string))
        with open(storage_string, 'w') as storage_file:
            storage_file.write(output)
        self.permits[user_id][prob_id][-1]['storage_file'] = storage_string
        now = time.time()
        output_file = '%s/problems/%s/%s' % (
            self.contest_dir, prob_id,
            self.permits[user_id][prob_id][-1]['output_file'])
        with open(output_file, 'r') as out_file:
            result = out_file.read().strip() == output.strip()
            self.permits[user_id][prob_id][-1]['correct'] = result
            self.permits[user_id][prob_id][-1]['time'] = now
            self.contest.submit_result(user_id, prob_id, now, result)
            return result

    def rejudge_problem(self, prob_id):
        """Regrade all submissions for a given problem

        Parameters:
            prob_id - problem to check outputs for
            output - output to test against correct output
        """
        self.contest.nullify_prob(prob_id)
        for user_id in self.permits:
            for submission in self.permits[user_id][prob_id]:
                if 'storage_file' in submission:
                    storage_string = submission['storage_file']
                    output_file = '%s/problems/%s/%s' % (
                        self.contest_dir, prob_id,
                        submission['output_file'])
                    with open(output_file, 'r') as out_file:
                        with open(storage_string, 'r') as storage_file:
                            result = out_file.read().strip() == storage_file.read().strip()
                            submission['correct'] = result
                            self.contest.submit_result(user_id, prob_id,
                                                       submission['time'], result)
