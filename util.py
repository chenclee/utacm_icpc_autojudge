import subprocess
import os
import threading


class TimeoutCommand(object):
    def __init__(self):
        self.process = None
        self.output = None

    def run(self, cmd, stdin, timeout):
        def target():
            self.process = subprocess.Popen(cmd, stdin=stdin,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.output = self.process.communicate()

        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()

        thread.join(timeout)
        if thread.is_alive():
            self.process.terminate()
            thread.join()
        return self.process.returncode, self.output[0]
