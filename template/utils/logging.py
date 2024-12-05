
import os
import logging
import bittensor as bt
import pandas as pd
from datetime import datetime

from typing_extensions import List
from logging.handlers import RotatingFileHandler

from template.protocol import BitrecsRequest


EVENTS_LEVEL_NUM = 38
DEFAULT_LOG_BACKUP_COUNT = 10


def setup_events_logger(full_path, events_retention_size):
    logging.addLevelName(EVENTS_LEVEL_NUM, "EVENT")

    logger = logging.getLogger("event")
    logger.setLevel(EVENTS_LEVEL_NUM)

    def event(self, message, *args, **kws):
        if self.isEnabledFor(EVENTS_LEVEL_NUM):
            self._log(EVENTS_LEVEL_NUM, message, args, **kws)

    logging.Logger.event = event

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        os.path.join(full_path, "events.log"),
        maxBytes=events_retention_size,
        backupCount=DEFAULT_LOG_BACKUP_COUNT,
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(EVENTS_LEVEL_NUM)
    logger.addHandler(file_handler)

    return logger




timestamp_file = 'timestamp.txt'

def write_timestamp(current_time):
    tmp_file = timestamp_file + '.tmp'
    with open(tmp_file, 'w') as f:
        f.write(str(current_time))
    os.replace(tmp_file, timestamp_file)  # Atomic operation to replace the file


def read_timestamp():
    try:
        with open(timestamp_file, 'r') as f:
            timestamp_str = f.read()
            return float(timestamp_str)
    except (FileNotFoundError, ValueError):
        return None


def remove_timestamp_file():
    if os.path.exists(timestamp_file):
        os.remove(timestamp_file)


def log_miner_responses(full_path: str, step: int, responses: List[BitrecsRequest]) -> None:
    try:
        
        frames = []
        for response in responses:
            headers = response.to_headers()
            df = pd.json_normalize(headers)
            #print(df.head())
            #bt.logging.info(f"Miner response: {df.head()}")
            frames.append(df)
        final = pd.concat(frames)

        p = os.path.join(full_path, 'miner_responses')
        if not os.path.exists(p):
            os.makedirs(p)
        
        if len(final) > 0:
            #dt = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            #full_path = os.path.join(p, f'miner_responses_step_{step}_{dt}.csv')
           
            full_path = os.path.join(os.path.pwd(), f'miner_responses_step_{step}.csv')
            final.to_csv(full_path, index=False)

        bt.logging.info(f"Miner responses logged {len(final)}")
    
    except Exception as e:
        bt.logging.error(f"Error in logging miner responses: {e}")
        
    
    