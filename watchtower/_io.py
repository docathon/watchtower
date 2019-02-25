import pandas as pd
import os


def _update_and_save(filename, raw, old_raw=None):
    """
    """
    if old_raw is not None:
        raw = pd.concat([raw, old_raw], ignore_index=True)
        if "id" in raw.columns:
            subset_column = "id"
        elif "sha" in raw.columns:
            subset_column = "sha"
        else:
            raise ValueError("No known column to distinguish subsets")
        raw = raw.drop_duplicates(subset=[subset_column])
    try:
        os.makedirs(os.path.dirname(filename))
    except OSError:
        pass
    raw.to_json(filename, date_format="iso")
