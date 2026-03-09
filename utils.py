import pandas as pd

def safe_dataframe(data, columns=None):
    if data:
        return pd.DataFrame(data)
    return pd.DataFrame(columns=columns if columns else [])