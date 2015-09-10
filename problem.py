import os

class Problem:

    def __init__(self, prob_id, contest_dir, logger):
        self.prob_id = prob_id
        self.prob_path = os.path.join(contest_dir, 'problems', prob_id)
        self.logger = logger
        self.reload_files()

    def reload_files(self):
        """Load problem from file. This includes the config file and the
        problem statement.
        """
        self.logger.info("Loading files for problem: " + self.prob_id)
        try:
            with open(os.path.join(self.prob_path, 'content.html'), 'r') as in_file:
                self.content = in_file.read()
        except Exception as e:
            self.logger.warn("Error loading problem content: " + e.message)
            self.content = """
                <h1>Oops</h1>
                <img src="http://i2.kym-cdn.com/entries/icons/original/000/000/043/disaster-girl.jpg">
            """

        try:
            with open(os.path.join(self.prob_path, 'config.txt'), 'r') as in_file:
                config = eval(in_file.read())
                self.logger.debug("config: " + str(config))
                try:
                    self.time_limit = float(config['time_limit'])
                    self.logger.debug("Time limit: %.1f sec" % self.time_limit)
                except Exception as e:
                    self.logger.warn("Error reading time_limit. Using default (3.0 sec)")
                    self.time_limit = 3.0
                try:
                    self.mem_limit = int(config['mem_limit'])
                    self.logger.debug("Memory limit: %d mb" % self.mem_limit)
                except Exception as e:
                    self.logger.warn("Error reading mem_limit. Using default (64 mb)")
                    self.mem_limit = 64
                try:
                    judge_data = config['judge_data']
                    self.inputs = [data[0] for data in judge_data]
                    self.outputs = [data[1] for data in judge_data]
                    self.logger.debug("Inputs: %s" % str(self.inputs))
                    self.logger.debug("Outputs: %s" % str(self.outputs))
                except:
                    self.logger.error("Error reading judge_data. Using default ([('input.txt', 'output.txt')])")
                    self.inputs = ['input.txt']
                    self.outputs = ['output.txt']
        except Exception as e:
            self.logger.warn("Error loading problem config: " + e.message)
            self.logger.warn("Using default time limit (3.0 sec)")
            self.time_limit = 3.0
            self.logger.warn("Using default memory limit (64 mb)")
            self.mem_limit = 64
            self.inputs = ['input.txt']
            self.outputs = ['output.txt']

        try:
            with open(os.path.join(self.prob_path, self.inputs[0]), 'r') as in_file:
                self.input_text = in_file.read()
            with open(os.path.join(self.prob_path, self.outputs[0]), 'r') as in_file:
                self.output_text = in_file.read()
        except Exception as e:
            self.logger.critical("No input/output files found for " + self.prob_id)
            raise
