from io import StringIO
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

def load_html(filenames: list, directory: str) -> pd.DataFrame:
    """
    Loads multiple HTML files containing tables from a directory and 
    concatenates them into a single DataFrame. Mirrors load_raw but 
    for HTML files instead of CSVs.
    
    Args:
        filenames (list): List of filenames (with .html extension).
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

        with open(file, "r", encoding="utf-8") as f:
            html_content = f.read()

        # Extract year from filename e.g. "us_vehicle_registrations_2023.html"
        year = int(filename.split("_")[-1].replace(".html", ""))

        df = pd.read_html(StringIO(html_content), flavor="html5lib")[0]
        df["year"] = year
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
        dataframes.append(df)

    if not dataframes:
        raise ValueError("No valid files were loaded.")

    combined_df = pd.concat(dataframes, ignore_index=True)
    return combined_df

def load_txdmv_pdf(path: str, page_index: int = 16) -> pd.DataFrame:
    """
    Extracts the year-over-year vehicle registration table from the 
    TxDMV Alternatively Fueled Vehicle Report PDF.
    
    Args:
        path (str): Path to the PDF file.
        page_index (int): Zero-based page index of the table (default 16 = page 17).
        
    Returns:
        pd.DataFrame: Long-format DataFrame with columns: fuel_type, year, registered_vehicles.
    """
    import pdfplumber

    with pdfplumber.open(path) as pdf:
        table = pdf.pages[page_index].extract_table()

    years = [col for col in table[0] if col and col.startswith("FY")]
    data_rows = [row for row in table[3:] if row[0] and row[0].strip() not in ("", None)]

    long_rows = []
    for row in data_rows:
        fuel = row[0].replace("\n", " ").strip()
        values = [row[i] for i in range(1, len(row), 3)]
        for year, val in zip(years, values):
            long_rows.append({
                "fuel_type": fuel,
                "year": int(year.replace("FY ", "").strip()),
                "registered_vehicles": val
            })

    df = pd.DataFrame(long_rows)
    df["registered_vehicles"] = (
        df["registered_vehicles"]
        .fillna("0")
        .str.replace(",", "", regex=False)
        .str.replace("-", "0", regex=False)
        .str.strip()
        .astype(float)
    )

    return df