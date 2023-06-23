import logging

# Set the log level
logging.basicConfig(level=logging.INFO)

# Create a logger instance
logger = logging.getLogger()

# Set the log format
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)
