import os
import pandas as pd

def for_each_csv(folder_path, func):
    """
    Applies func(df, filename) to every CSV in folder_path
    """
    results = []

    for filename in os.listdir(folder_path):
        if filename.endswith(".csv"):
            file_path = os.path.join(folder_path, filename)
            df = pd.read_csv(file_path)

            output = func(df, filename)
            if output is not None:
                results.append(output)

    return results
