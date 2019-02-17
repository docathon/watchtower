import pandas as pd
import os


def _update_and_save(filename, raw, old_raw=None):
    """
    """
    if old_raw is not None:
        raw = pd.concat([raw, old_raw], ignore_index=True)
        raw = raw.drop_duplicates(subset=['id'])
    try:
        os.makedirs(os.path.dirname(filename))
    except OSError:
        pass
    raw.to_json(filename, date_format="iso")
