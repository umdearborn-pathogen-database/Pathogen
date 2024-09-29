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
