import datetime
import logging
import os


class AppLogger:
    # Custom file handler that recreates log files if deleted during runtime
    class CustomFileHandler(logging.FileHandler):
        def emit(self, record):
            try:
                # Check if the log file still exists
                if not os.path.exists(self.baseFilename):
                    # Create the directory if it does not exist
                    os.makedirs(os.path.dirname(
                        self.baseFilename), exist_ok=True)
                    # Reopen the log file
                    self.stream = self._open()

                # Write the log record
                super().emit(record)
            except FileNotFoundError:
                # Handle case where directory is deleted
                os.makedirs(os.path.dirname(self.baseFilename), exist_ok=True)
                self.stream = self._open()
                super().emit(record)

    def __init__(self, log_dir='logs'):
        # Initialize logger configuration
        self.date = datetime.datetime.now().strftime('%Y-%m-%d')
        self.log_dir = log_dir
        self.log_file = f"app-{self.date}.log"
        self.logger = self.setup_logger()

    def setup_logger(self):
        # Ensure the log directory exists
        os.makedirs(self.log_dir, exist_ok=True)

        # Create and configure the logger
        logger = logging.getLogger('app_logger')
        logger.setLevel(logging.DEBUG)
        # Prevent log messages from propagating to the root logger
        logger.propagate = False

        # Define the log file path
        log_file_path = os.path.join(self.log_dir, self.log_file)

        # Create a custom file handler for logging to a file
        file_handler = self.CustomFileHandler(log_file_path, mode='a')
        file_handler.setLevel(logging.DEBUG)

        # Create a console handler for logging to the terminal
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        # Create a log format for both handlers
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add the handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        # Log a startup message to confirm setup
        logger.info("Logger setup complete. Log file: %s", log_file_path)

        return logger

    def get_logger(self):
        # Return the configured logger instance
        return self.logger
