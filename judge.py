import datetime
import uuid


class Judge:
    contest = null          # contest pointer
    permit_ids = []         # map of permits and associated values
    problem_configs = {}    # problem configurations such as input
    person_runs = {}        # list of person's runs so far

    def __init__(self, contest, prob_ids):
        """Read in config files for problem set

        Parameters:
            contest  - pointer to contest object
            prob_ids - prob_ids
        """
        this.contest = contest
        # read in configuration files
        for id in prob_ids:
            problem_configs[id] = readConfig(id)

    def readConfig(prob_id):
        """Read configuration file for a problem statement

        Parameter:
            prob_id - problem id to load configuration for

        return - dictionary of configuration parameters
        """
        configuration = {}
        with open('problems/{0}/config.txt'.format(id)) as file:
            configuration = eval(file.read())
        return configuration

    def get_expiring_permit(self, user_id, prob_id):
        """Return a unique id and keep a record of its expiration date

        Parameters:
            user_id - unique user id
            prob_id - problem statement id

        return - returns unique id for specific problem run
        """
        if prob_id not in person_runs:
            person_runs[prob_id] = []
        if len(person_runs[prob_id]) == problem_configs[prob_id]["max_attemps"]:
            return None
        # if another attempt is valid, generate uuid and store data
        id = uuid.uuid1()
        time = contest.remainging_time() - \
            problem_configs[prob_id]["time_allowed"]
        run_data = {}
        run_data["permit_id"] = id
        run_data["due_time"] = time
        run_data["user_id"] = user_id
        run_data["prob_id"] = prob_id
        permit_ids[id] = run_data
        return id

    def valid_permit(self, permit):
        """Test whether a permit is valid
        (eg exists and has not expired)

        Parameter:
            permit - unique id for specific run case

        return - true if permit is valid and false otherwise
        """
        current_time = contest.remainging_time()
        if current_time < permit_ids[permit]["due_time"]:
            return false
        else:
            return true

    def get_input_text(self, permit):
        """Return input file data for user to run program on

        Parameter:
            permit - unique id for specific run case

        return - test data for user to run their program on
        """
        for input_file, output_file in\
                problem_configs[permit_ids[permit]["prob_id"]]["inputs"]:
            if input_file not in person_runs[permit_ids[permit]["prob_id"]]:
                person_runs[permit_ids[permit]["prob_id"]].append(input_file)
                permit_ids[permit]["input_file"] = input_file
                permit_ids[permit]["output_file"] = output_file
                with open("problems/{0}/{1}".format(
                        permit_ids[permit]["prob_id"], input_file)) as f:
                    return f.read()

    # test output sent by user
    def enqueue_submission(self, permit, source, output):
        """Test output sent from contestant

        Parameters:
            permit - unique id for specific test run
            source - source code
            output - output to test against correct output

        return - true if output was correct and false otherwise
        """
        if not valid_permit(permit):
            return false
        with open("problems/{0}/{1}".format(
                permit_ids[permit]["prob_id"],
                permit_ids[permit]["output_file"])) as f:
            if f.read() == output:
                permit_ids[permit]["result"] = true
                return true
            else:
                permit_ids[permit]["result"] = false
                return false
