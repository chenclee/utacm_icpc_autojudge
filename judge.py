import time
import os
import pickle
import datetime
import sqlite3 as lite


class Judge:

    def __init__(self, contest, prob_ids, contest_dir, database, contest_name):
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
        self.contest_dir = contest_dir
        self.contest_name = contest_name
        self.prob_cfgs = (
            {prob_id: self.load_cfg(prob_id) for prob_id in prob_ids})
        self.submitted_runs = {}
        self.connection = lite.connect(database)
        self.cursor = self.connection.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS names(uuid INTEGER PRIMARY KEY, name TEXT, email TEXT)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS %s (uuid INTEGER, problem TEXT, attempt INTEGER, input_file TEXT, output_file TEXT, expiration REAL, time REAL, storage_file TEXT, correct INTEGER, UNIQUE(uuid, problem, attempt))" % contest_name)
        self.cursor.execute("CREATE INDEX IF NOT EXISTS emails on names(email)")

    def get_uuid(self, user_id):
        self.cursor.execute("SELECT * FROM names WHERE email=?", (str(user_id[0]),))
        return self.cursor.fetchone()[0]

    def get_max_attempt(self, uuid, prob_id):
        self.cursor.execute("SELECT attempt FROM %s WHERE uuid=? AND problem=? ORDER BY attempt DESC" % self.contest_name, (uuid, prob_id))
        r = self.cursor.fetchone()
        return r[0] if r else -1

    def load_cfg(self, prob_id):
        """Read configuration file for a problem statement

        Parameter:
            prob_id - problem id to load configuration for

        return - dictionary of configuration parameters
        """
        path = '%s/problems/%s/config.txt' % (self.contest_dir, prob_id)
        with open(path, 'r') as in_file:
            return eval(in_file.read())

    def get_expiring_permit(self, user_id, prob_id, create=True):
        """Return a unique id and keep a record of its expiration date

        Parameters:
            user_id - unique user id
            prob_id - problem statement id

        Return - returns {'is_new', 'ttl'} or None if the max number
                 of permits for the user and problem has been reached.
        """
        self.cursor.execute("SELECT count(*) FROM names WHERE email=? GROUP BY uuid", (str(user_id[0]),))
        if self.cursor.fetchone() == None:
            self.cursor.execute("INSERT INTO names(uuid, name, email) VALUES (NULL, ?, ?)", (user_id[1], user_id[0]))

        now = time.time()
        uuid = self.get_uuid(user_id)
        attempt = self.get_max_attempt(uuid, prob_id)
        count = attempt + 1
        self.cursor.execute("SELECT correct, expiration from %s WHERE uuid=? AND problem=? AND attempt=?" % self.contest_name, (uuid, prob_id, attempt))
        r = self.cursor.fetchone()
        if attempt > -1:

            if r[0]:
                return "solved"

            ttl = r[1] - now
            if ttl > 0 and r[0] is None:
                return {'is_new': False, 'ttl': int(ttl)}

        if (attempt == self.prob_cfgs[prob_id]['max_attempts'] - 1):
            return None

        if not create:
            return None

        # if another attempt is valid, generate uuid and store data
        permit_num = count
	self.cursor.execute("INSERT INTO %s (uuid, problem, attempt, input_file, output_file, expiration) VALUES((SELECT uuid FROM names WHERE email=?), ?, ?, ?, ?, ?)" % self.contest_name,
	    (user_id[0], prob_id, count, self.prob_cfgs[prob_id]['inputs'][count], self.prob_cfgs[prob_id]['outputs'][count], now + self.prob_cfgs[prob_id]['time_allowed']))
        return {'is_new': True, 'ttl': int(self.prob_cfgs[prob_id]['time_allowed'])}

    def get_solved_problems(self, user_id):
        solved = {}
        for prob_id in self.prob_cfgs:
            try:
                uuid = self.get_uuid(user_id)
                self.cursor.execute("SELECT correct FROM %s WHERE uuid=? AND prob_id=? AND correct=1" % contest_name, (uuid, prob_id))
                solved[prob_id] = self.cursor.fetchone() != None
            except:
                solved[prob_id] = False
        return solved

    def get_remaining_permit_counts(self, user_id):
        remaining_counts = {}
        for prob_id in self.prob_cfgs:
            try:
                attempt = self.get_max_attempt(self.get_uuid(), prob_id)
                remaining_counts[prob_id] = self.prob_cfgs[prob_id]['max_attempts'] - attempt - 1
            except:
                remaining_counts[prob_id] = self.prob_cfgs[prob_id]['max_attempts']
        return remaining_counts

    def get_problems_time_to_solve(self):
        times = {}
        for prob_id in self.prob_cfgs:
            times[prob_id] = self.prob_cfgs[prob_id]['time_allowed']
        return times

    def valid_permit(self, user_id, prob_id):
        """Test whether a permit is valid
        (eg exists and has not expired)

        Parameter:
            user_id - owner of the permit
            prob_id - problem the permit is for

        return - true if permit is valid and false otherwise
        """
        now = time.time()
        uuid = self.get_uuid(user_id)
        self.cursor.execute("SELECT expiration, correct FROM %s WHERE uuid = ? AND problem = ?" % self.contest_name, (uuid, prob_id))
        rows = self.cursor.fetchall()
        if(rows != None):
            for i in rows:
                if now < i[0] and i[1] == None:
                        return True
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

        uuid = self.get_uuid(user_id)
        self.cursor.execute("SELECT input_file FROM %s WHERE uuid=? AND problem=? ORDER BY attempt DESC" % self.contest_name, (uuid, prob_id))
        in_str = self.cursor.fetchone()[0]
        input_file = '%s/problems/%s/%s' % (
            self.contest_dir, prob_id,
            in_str)
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
        now = time.time()
        uuid = self.get_uuid(user_id)
        attempt = self.get_max_attempt(uuid, prob_id)
        if not self.valid_permit(user_id, prob_id):
            return None
        output = '\n'.join([line.strip('\n\r ') for line in output.splitlines()])
        self.cursor.execute("SELECT output_file FROM %s WHERE uuid=? AND problem=? ORDER BY attempt DESC" % self.contest_name, (uuid, prob_id))
        out_str = self.cursor.fetchone()[0]
        storage_string = '%s/submissions/%s/%s/%s' % (
            self.contest_dir, prob_id, user_id,
            out_str)
        self.cursor.execute("SELECT output_file FROM %s WHERE uuid=? AND problem=? ORDER BY attempt DESC" % self.contest_name, (uuid, prob_id))
        source_string = '%s/submissions/%s/%s/%s.source' % (
            self.contest_dir, prob_id, user_id,
            out_str)
        output_file = '%s/problems/%s/%s' % (
            self.contest_dir, prob_id,
            out_str)
        self.cursor.execute("UPDATE %s SET time = ?, storage_file = ? WHERE uuid= ? AND problem = ? AND attempt = ?" % self.contest_name,
	    ( now, storage_string, uuid, prob_id, attempt))
        if not os.path.exists(os.path.dirname(storage_string)):
            os.makedirs(os.path.dirname(storage_string))
        with open(source_string, 'w') as storage_file:
            storage_file.write(source)
        with open(storage_string, 'w') as storage_file:
            storage_file.write(output)
        self.cursor.execute("")
        self.cursor.execute("SELECT output_file FROM %s WHERE uuid=? AND problem=? ORDER BY attempt DESC" % self.contest_name, (uuid, prob_id))
        with open(output_file, 'r') as out_file:
            out_file_string = '\n'.join([line.strip('\n\r ') for line in out_file.readlines()])
            result = out_file_string.strip() == output.strip()
            self.contest.submit_result(user_id, prob_id, now, result)
	    self.cursor.execute("UPDATE %s SET correct = ?, time = ?, storage_file = ? WHERE uuid= ? AND problem = ? AND attempt = ?" % self.contest_name,
		(result, now, storage_string, uuid, prob_id, attempt))
            return result

    def rejudge_problem(self, prob_id):
        """Regrade all submissions for a given problem

        Parameters:
            prob_id - problem to check outputs for
            output - output to test against correct output
        """
        print prob_id
        self.cursor.execute("SELECT uuid, storage_file, output_file, time, attempt FROM %s WHERE problem=? ORDER BY uuid ASC, problem ASC, attempt ASC" % self.contest_name, (str(prob_id), ))
        rows = self.cursor.fetchall()
        self.contest.nullify_prob(prob_id)
        for row in rows:
            if(row[1] != None):
                storage_string = row[1]
                output_file = '%s/problems/%s/%s' % (
                    self.contest_dir, prob_id,
                    row[2])
                with open(output_file, 'r') as out_file:
                    with open(storage_string, 'r') as storage_file:
                        result = out_file.read().strip() == storage_file.read().strip()
                        self.cursor.execute("UPDATE %s SET correct=? WHERE uuid=? AND problem=? AND attempt=?" % self.contest_name,
                                (result, row[0], prob_id, row[4]))
                        self.cursor.execute("SELECT email, name FROM names WHERE uuid=?", (row[0],))
                        user = self.cursor.fetchone()
                        user_id = (user[0], user[1])
                        self.contest.submit_result(user_id, prob_id,
                                    row[3], result)

    def save_data(self):
        """Pickle permit data structure"""
        self.connection.commit()
        self.connection.close()
