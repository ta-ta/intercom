import logging
import logging.handlers
import os

import env.local as CONFIG

PATH = os.path.dirname(os.path.abspath(__file__))


logfile = os.path.join(PATH, 'log/intercom.log')
formatter = logging.Formatter(
    '[%(asctime)s] %(levelname)s %(message)s')

logger = logging.getLogger(CONFIG.LOG_INTERCOM)
logger.setLevel(logging.DEBUG)

handler = logging.handlers.TimedRotatingFileHandler(
    filename=logfile, when='D', backupCount=30,
)
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
logger.addHandler(handler)
