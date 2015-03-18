import os

class Problem:

    def __init__(self, prob_id, contest_dir, logger):
        self.prob_id = prob_id
        self.prob_path = os.path.join(contest_dir, 'problems', prob_id)
        self.logger = logger
        self.reload()

    def reload(self):
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
                try:
                    self.time_limit = float(config['time_limit'])
                    self.logger.debug("Time limit: %.1f sec" % self.time_limit)
                except Exception as e:
                    self.logger.warn("Error reading time_limit. Using default (2.0 sec)")
                    self.time_limit = 2.0
                try:
                    self.mem_limit = int(config['mem_limit'])
                    self.logger.debug("Memory limit: %d mb" % self.mem_limit)
                except Exception as e:
                    self.logger.warn("Error reading mem_limit. Using default (256 mb)")
                    self.mem_limit = 256
                try:
                    self.output_limit = int(config['output_limit'])
                    self.logger.debug("Output limit: %d lines" % self.output_limit)
                except Exception as e:
                    self.logger.warn("Error reading output_limit. Using default (10000 lines)")
                    self.output_limit = 10000
        except Exception as e:
            self.logger.warn("Error loading problem config: " + e.message)
            self.logger.warn("Using default time limit (2.0 sec)")
            self.time_limit = 2.0
            self.logger.warn("Using default memory limit (256 mb)")
            self.mem_limit = 256
            self.logger.warn("Using default output limit (10000 lines)")
            self.output_limit = 10000
