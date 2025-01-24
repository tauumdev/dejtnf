import datetime
import os
import logging

#  v0.3.0
# class CommunicationLogFileHandler(logging.Handler):
#     def __init__(self, path, prefix=""):
#         logging.Handler.__init__(self)

#         self.path = path
#         self.prefix = prefix

#     def emit(self, record):
#         filename = os.path.join(self.path, "{}_{}_{}.log".format(
#             self.prefix, record.address, record.session_id))
#         os.makedirs(os.path.dirname(filename), exist_ok=True)
#         with open(filename, 'a') as f:
#             f.write(self.format(record) + "\n")


#  v0.1.0
class CommunicationLogFileHandler(logging.Handler):
    def __init__(self, path, prefix=""):
        logging.Handler.__init__(self)

        self.path = path
        self.prefix = prefix
        self.date = datetime.datetime.now().strftime('%Y-%m-%d')

    def emit(self, record):
        filename = os.path.join(
            self.path, "{}-{}.log".format(record.remoteName, self.date))
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'a') as f:
            f.write(self.format(record) + "\n")
