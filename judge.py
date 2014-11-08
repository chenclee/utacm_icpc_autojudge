import datetime
import uuid


class Judge:
    @staticmethod
    def load_cfg(prob_id):
        """Read configuration file for a problem statement

        Parameter:
            prob_id - problem id to load configuration for

        return - dictionary of configuration parameters
        """
        with open('problems/{0}/config.txt'.format(prob_id)) as in_file:
            return eval(in_file.read())

    def __init__(self, contest, prob_ids):
        """Read in config files for problem set

        contest - pointer to contest state obj
        permits - dict mapping users to problems to permits issued
        prob_cfgs - dict mapping problems to problem configurations
        submitted_runs - ???

        Parameters:
            contest  - pointer to contest object
            prob_ids - prob_ids
        """
        self.contest = contest
        self.permits = {}
        self.prob_cfgs = {prob_id: load_cfg(prob_id) for prob_id in prob_ids}
        self.submitted_runs = {}

    def get_expiring_permit(self, user_id, prob_id):
        """Return a unique id and keep a record of its expiration date

        Parameters:
            user_id - unique user id
            prob_id - problem statement id

        Return - returns (unique id, ttl) or None if the max number
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
            if ttl > 0:
                return (last_permit['permit_uid'], int(ttl))

        if (len(self.permits[user_id][prob_id])
                == self.prob_cfgs[prob_id]['max_attempts']):
            return None

        # if another attempt is valid, generate uuid and store data
        permit_num = len(self.permits[user_id][prob_id])
        permit_uid = uuid.uuid1()
        self.permits[user_id][prob_id].append({
            'permit_uid': permit_uid,
            'expiration': now + self.prob_cfgs[prob_id]['time_allowed'],
            'input_file': self.prob_cfgs[prob_id]['inputs'][permit_num],
            'output_file': self.prob_cfgs[prob_id]['outputs'][permit_num],
            'correct': False
        })
        return permit_uid

    def valid_permit(self, user_id, prob_id, permit_uid):
        """Test whether a permit is valid
        (eg exists and has not expired)

        Parameter:
            user_id - owner of the permit
            prob_id - problem the permit is for
            permit_uid - unique identifier

        return - true if permit is valid and false otherwise
        """
        now = time.time()
        if (user_id in self.permits
                and prob_id in self.permits[user_id]
                and len(self.permits[user_id][prob_id]) > 0):
            return now > self.permits[user_id][prob_id][-1]['expiration']
        return False

    def get_input_text(self, user_id, prob_id, permit_uid):
        """Return input file data for user to run program on

        Parameter:
            user_id - user requesting the input file
            prob_id - problem the user is request input for
            permit_uid - unique identifier

        return - test data for user to run their program on
        """
        if not valid_permit(user_id, prob_id, permit_uid):
            return None

        assert self.permits[user_id][prob_id][-1]['permit_uid'] == permit_uid

        input_file = 'problems/%s/%s' % (
            prob_id, self.permits[user_id][prob_id][-1]['input_file'])
        with open(input_file, 'r') as in_file:
            return in_file.read()

    # test output sent by user
    def enqueue_submission(self, user_id, prob_id, permit_uid, source, output):
        """Test output sent from contestant

        Parameters:
            user_id - user who is submitting output
            prob_id - problem the user is submitting output for
            permit_uid - unique identifier
            source - source code
            output - output to test against correct output

        return - true if output was correct and false otherwise
        """
        if not valid_permit(user_id, prob_id, permit_uid):
            return None

        output_file = 'problems/%s/%s' % (
            prob_id, self.permits[user_id][prob_id][-1]['output_file'])
        with open(output_file, 'r') as out_file:
            if out_file.read().strip() == output.strip():
                self.permits[user_id][prob_id]['correct'] = True
                return True
            else:
                return False
