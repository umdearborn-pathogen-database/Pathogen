import pandas as pd

def print_dataframe_summary(df_list):
    print("type")
    print(type(df_list))
    for idx, df in enumerate(df_list):
        print("type of df")
        print(type(df))
        print(f"\nDataFrame {idx + 1}:")
        print("-" * 50)
        
        # Number of rows and columns
        print(f"Shape: {df.shape}")
        
        # Column names
        print(f"Columns: {df.columns.tolist()}")
        
        # Data types of each column
        print("\nData types:")
        print(df.dtypes)
        
        # Basic statistics for numeric columns
        print("\nBasic statistics:")
        print(df.describe())  # Only applies to numeric columns
        
        # Count of missing values per column
        print("\nMissing values per column:")
        print(df.isnull().sum())
        
        print("-" * 50)

        # Review of some pandas dataframe concepts
        print("df")
        print(df)

        # print("sum down each column (default = axis = 0)")
        # print(df.sum(axis=0))

        # print("sum accross each row")
        # print(df.sum(axis=1))

        # Apply np.sqrt column-wise (default behavior)
        # print(df.apply(np.sqrt))  # Equivalent to df.apply(np.sqrt, axis=0)

        # Apply np.sqrt row-wise
        # print(df.apply(np.sqrt, axis=1))

# Example usage:
# Assuming df_list is a list of DataFrames
# df_list = [df1, df2, df3]
# print_dataframe_summary(df_list)

# def add_bacteria_column(mass_spec_data_list, meta_data_list):
#     """
#     Add the 'Bacteria' column from the meta data to each corresponding DataFrame
#     in the mass spec data list.
    
#     Parameters:
#     - mass_spec_data_list: List of pandas DataFrames containing mass spec data.
#     - meta_data_list: List of pandas DataFrames containing meta data with 'Bacteria' column.
    
#     Returns:
#     - List of pandas DataFrames with the 'Bacteria' column added.
#     """
#     updated_mass_spec_data = []
#     print(f"type of mass_spec_data_list: {type(mass_spec_data_list)}")
#     print(f"shape of first mass_spec DataFrame: {mass_spec_data_list[0].shape if len(mass_spec_data_list) > 0 else 'Empty List'}")
#     print(f"type of meta_data_list: {type(meta_data_list)}")
#     print(f"shape of first meta_data DataFrame: {meta_data_list[0].shape if len(meta_data_list) > 0 else 'Empty List'}")
#     for mass_spec_df, meta_df in zip(mass_spec_data_list, meta_data_list):
#         if 'Bacteria' in meta_df.columns:
#             # Add the 'Bacteria' column to the mass spec DataFrame
#             mass_spec_df['Bacteria'] = meta_df['Bacteria'].values[0]
#         updated_mass_spec_data.append(mass_spec_df)
    
#     return updated_mass_spec_data

def add_bacteria_column(df_main, mass_spec_data_list):
    """
    Adds the 'Bacteria' column value from the main DataFrame to the corresponding 
    DataFrames in the mass_spec_data_list.
    
    Parameters:
    - df_main (pd.DataFrame): DataFrame containing columns 'patientID', 'Bacteria', etc.
    - mass_spec_data_list (list): List of pandas DataFrames where 'Bacteria' column will be added.
    
    Returns:
    - List of pandas DataFrames with the 'Bacteria' column added.
    """
    # Ensure that the number of rows in the main DataFrame matches the number of DataFrames in the list
    if len(df_main) != len(mass_spec_data_list):
        raise ValueError("The number of rows in the main DataFrame must match the number of DataFrames in the list.")
    print(type(df_main))
    print(df_main[0].shape)
    print(type(mass_spec_data_list))
    print(mass_spec_data_list.shape)
    # Iterate over the mass_spec_data_list and add the 'Bacteria' column from df_main
    for i, spectrum_df in enumerate(mass_spec_data_list):
        # Skip the header row (first row) in df_main
        bacteria_value = df_main[i + 1]['Bacteria']  # +1 to skip the header row
        spectrum_df['Bacteria'] = bacteria_value
    
    return mass_spec_data_list

# def merge_metadata_with_raw_data(dataframes, metadata):
#     """
#     Merges a list of raw data DataFrames with a metadata DataFrame.

#     Parameters:
#     dataframes (list): A list of DataFrames containing raw data.
#     metadata (DataFrame): A DataFrame containing metadata.

#     Returns:
#     DataFrame: A single DataFrame with merged data.
#     """
#     merged_dataframes = []

#     for raw_data in dataframes:
#         # Extract patientID.orig from the first row of the raw data
#         # Assuming the filename or a specific column contains this information
#         patientID_orig = raw_data['source_file'].str.split('-').str[-1].iloc[0]  # Modify as needed
#         bacteria_value_orig = raw_data['source_file'].str.split('-').str[-2].iloc[0]

#         # Find the corresponding row in the metadata
#         # Find the corresponding row in the metadata
#         matching_metadata = metadata[
#             (metadata['run'] == patientID_orig) &
#             (metadata['Bacteria'] == bacteria_value_orig)
#         ]
      
#         # If a match is found, merge the metadata with the raw data
#         if matching_metadata is not None and isinstance(matching_metadata, pd.DataFrame) and not matching_metadata.empty:
#             merged_data = raw_data.assign(
#                 patientID=matching_metadata['patientID'].values[0],
#                 patientID_orig=matching_metadata['patientID.orig'].values[0],
#                 experiment=matching_metadata['experiment'].values[0],
#                 location=matching_metadata['location'].values[0],
#                 Bacteria=matching_metadata['Bacteria'].values[0],
#                 run=matching_metadata['run'].values[0]
#             )
#             merged_dataframes.append(merged_data)

#     # Concatenate all merged DataFrames into one
#     final_data = pd.concat(merged_dataframes, ignore_index=True)
#     return final_data

def add_run_column_from_patientID(df):
    """
    Adds a 'run' column to the DataFrame by extracting the last part of 'patientID.orig'.

    Parameters:
    df (pd.DataFrame): The input DataFrame with columns ['patientID', 'patientID.orig', 'experiment', 'location', 'Bacteria'].

    Returns:
    pd.DataFrame: The updated DataFrame with the 'run' column added.
    """
    # Check if the necessary column exists
    if 'patientID.orig' not in df.columns:
        raise ValueError("DataFrame must contain a 'patientID.orig' column.")
    
    # Create the 'run' column by extracting the last part from 'patientID.orig'
    df['run'] = df['patientID.orig'].apply(lambda x: x.split('-')[-1])

    return df

def add_metadata_to_dataframes(dataframes, metadata):
    """
    Adds corresponding metadata to each DataFrame in the list.

    Parameters:
    dataframes (list of pd.DataFrame): List of DataFrames to which metadata will be added.
    metadata (pd.DataFrame): DataFrame containing the metadata.

    Returns:
    list of pd.DataFrame: List of DataFrames with added metadata columns.
    """
    for i, df in enumerate(dataframes):
        # Get the corresponding row from the metadata
        metadata_row = metadata.iloc[i]
        
        # Add metadata as new columns to the DataFrame
        for col in metadata_row.index:
            df[col] = metadata_row[col]
    
    return dataframes

# rewriting this below
# def combine_dataframes_with_metadata(dataframes, metadata):
#     """
#     Combines each DataFrame with its corresponding metadata into tuples.

#     Parameters:
#     dataframes (list of pd.DataFrame): List of DataFrames.
#     metadata (pd.DataFrame): DataFrame containing the metadata.

#     Returns:
#     list of tuples: List of tuples where each tuple contains a DataFrame and its corresponding metadata row.
#     """
#     combined_data = []

#     for i, df in enumerate(dataframes):
#         metadata_row = metadata.iloc[i]
#         combined_data.append((df, metadata_row))

#     return combined_data

    # Example usage
    # dataframes_with_source_file = [...]  # Your list of DataFrames
    # metadata_file_with_run = pd.DataFrame(...)  # Your metadata DataFrame
    # combined_data = combine_dataframes_with_metadata(dataframes_with_source_file, metadata_file_with_run)

def combine_dataframes_with_metadata(dataframes, metadata):
    combined_df = pd.DataFrame()  # Initialize an empty DataFrame

    for i, df in enumerate(dataframes):
        metadata_row = metadata.iloc[i]
        for col in metadata_row.index:
            df[col] = metadata_row[col]
        
        # Append the updated DataFrame to combined_df
        combined_df = pd.concat([combined_df, df], ignore_index=True)

    return combined_df

def get_sample_names(spectra):
    """
    Extract sample names from the spectra.
    
    Parameters:
    spectra (list): List of spectrum objects.
    
    Returns:
    pd.Series: A Series of sample names.
    """
    return pd.Series([s['patientID'] for s in spectra])

def average_mass_spectra(spectra, labels):
    """
    Average the mass spectra based on labels.
    
    Parameters:
    spectra (list): List of spectrum objects.
    labels (pd.Series): Series of sample names corresponding to each spectrum.
    
    Returns:
    DataFrame: A DataFrame containing averaged spectra.
    """
    # Create a DataFrame to hold the spectra data
    spectrum_data = pd.DataFrame([s.intensity for s in spectra])  # Assuming each spectrum has an 'intensity' attribute
    spectrum_data['sample'] = labels
    
    # Group by the sample names and calculate the mean for each group
    averaged_spectra = spectrum_data.groupby('sample').mean().reset_index()
    
    return averaged_spectra

def sendValuesToDatabase(df):
    from Dependencies.Global import getConnection
    conn = getConnection()
    num = (df.shape[1] - 2)
    table = f"PathogensCOMP{num}"
    df.to_sql(table, conn, if_exists='append', index=False)

def getValuesFromDatabase(df):
    from Dependencies.Global import database
    from Dependencies.Global import printMessage
    num = (df.shape[1] - 2)
    table = f"PathogensCOMP{num}"
    statement = f"SELECT COUNT(*) FROM {table}"
    msg = database(statement, initialize=False, fetchOne=True)
    if msg[0] == 0:
        printMessage("info", f"Table: {table} is empty. First values have been added.")
        return None
    else:
        print(msg)
        printMessage("info", f"Fetching data from table: {table}...")
        from Dependencies.Global import getConnection
        conn = getConnection()
        df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
        return df