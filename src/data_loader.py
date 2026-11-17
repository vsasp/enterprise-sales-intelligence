from pathlib import Path
import logging
import pandas as pd

LOGGER = logging.getLogger(__name__)

def load_csv_files(folder):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    paths = sorted(folder.glob("*.csv"))
    if not paths:
        LOGGER.warning("No CSV files found in %s", folder)
        return pd.DataFrame()
    frames = []
    for path in paths:
        try:
            df = pd.read_csv(path)
            df["Source_File"] = path.name
            frames.append(df)
            LOGGER.info("Loaded %s (%s rows)", path.name, len(df))
        except Exception:
            LOGGER.exception("Could not read %s", path)
    if not frames:
        return pd.DataFrame()
    combined = pd.concat(frames, ignore_index=True, sort=False)
    combined.columns = [str(c).strip().replace(" ", "_") for c in combined.columns]
    return combined
