import os
import pandas as pd

def load_raw(filenames: list, directory: str) -> pd.DataFrame:
    """
    Loads mutiple CSV files from a directory and concatenates them into a single DataFrame.
    
    Args:
        filenames (list): list of filenames (with extension).
        directory (str): Directory path where files are stored. 
        
    Returns:
        pd.DataFrame: Combined DataFrame containing all the files.
    """
    dataframes = []

    for filename in filenames:
        file = os.path.join(directory, filename)

        if not os.path.exists(file):
            print(f"Warning: {file} not found in {directory}")
            continue

        df = pd.read_csv(file, low_memory=False)
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
        dataframes.append(df)

    if not dataframes:
        raise ValueError("No valid files were loaded.")
    
    combined_df = pd.concat(dataframes, ignore_index=True)
    return combined_df