from datetime import datetime
from config import LOG_TIME_FORMAT

def log(message):
    timestamp = datetime.now().strftime(LOG_TIME_FORMAT)
    print(f"[{timestamp}] {message}")
