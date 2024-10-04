import pandas as pd

def print_dataframe_summary(df_list):
    for idx, df in enumerate(df_list):
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
        # print("df")
        # print(df)

        # print("sum down each column (default = axis = 0)")
        # print(df.sum(axis=0))

        # print("sum accross each row")
        # print(df.sum(axis=1))

        ## Apply np.sqrt column-wise (default behavior)
        # print(df.apply(np.sqrt))  # Equivalent to df.apply(np.sqrt, axis=0)

        ## Apply np.sqrt row-wise
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