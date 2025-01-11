import os
import logging


class CommunicationLogFileHandler(logging.Handler):
    def __init__(self, path, prefix=""):
        logging.Handler.__init__(self)

        self.path = path
        self.prefix = prefix

    def emit(self, record):
        filename = os.path.join(self.path, "{}_{}_{}.log".format(
            self.prefix, record.address, record.session_id))
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'a') as f:
            f.write(self.format(record) + "\n")
