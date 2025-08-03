import os
import json
from datetime import datetime

LOG_PATH = "data/price_change_log.json"

def append_to_log(entry, path=LOG_PATH):
    history = []
    if os.path.exists(path):
        with open(path, "r") as f:
            history = json.load(f)

    entry["applied_on"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    history.append(entry)

    with open(path, "w") as f:
        json.dump(history, f, indent=2)
