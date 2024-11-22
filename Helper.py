import pandas as pd

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
    from Global import getConnection
    conn = getConnection()
    num = (df.shape[1] - 2)
    table = f"PathogensCOMP{num}"
    df.to_sql(table, conn, if_exists='append', index=False)

def getValuesFromDatabase(num_components):
    from Global import database
    from Global import printMessage
    table = f"PathogensCOMP{num_components}"
    statement = f"SELECT COUNT(*) FROM {table}"
    msg = database(statement, initialize=False, fetchOne=True)
    if (msg == None) or (msg[0] == 0):
        printMessage("info", f"Table: {table} is empty. First values have been added.")
        return None
    else:
        printMessage("info", f"Fetching data from table: {table}...")
        from Global import getConnection
        conn = getConnection()
        df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
        return df