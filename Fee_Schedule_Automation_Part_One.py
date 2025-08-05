# Introduction to the fee schedule program (welcome page for users)
welcome_message = """
--------------------------------------------------------------
           Fee Schedule Automation Program Part One
--------------------------------------------------------------
Loading files... Estimated load time: 2 minutes
"""
print(welcome_message)

print('Initiating Data Processing: Loading Physician File...')

# Import packages & libraries for data cleaning and processing
import pandas as pd
import numpy as np
import os, glob
import pathlib
import datetime

# Python program that will take in all physician files and process them into the desired format
def processor_text_physicians(file_path):

    # This code will read text files from the specified directory, create column headers to map out data correctly, specify deliminator, 
    # header does not exist, and skip the last four lines of code to ignore copyright infringement lines. Also added USA column: MOD2, which will have empty strings.
    imported_physician_text_files = pd.read_csv(file_path, names = ['Year', 'Carrier Number', 'LOCALITY', 'CPT', 'MOD1', 'PHYSICIANS-RATES', 'FACILITY-RATES', 'Filler', 'PCTC Indicator', 'Status Code', 
                'Multiple Surgery Indicator', '50% Therapy Reduction Amount', 'OPPS Indicator', 'OPPS Non Facility Fee Amount', 'TRAILER RECORD', 
                'Trailer Indicator', 'MOD2', 'STATE'], sep = ',', header = None, engine = 'python', skipfooter = 4)
     
    # Added USA columns such as MOD1 and MOD2 filled with null values (NaN)
    imported_physician_text_files[['MOD1', 'MOD2']] = imported_physician_text_files[['MOD1', 'MOD2']].replace(r'^\s*$', np.nan, regex=True)

    # Remove unnecessary columns, ignoring columns listed that in the ticket description
    imported_physician_text_files = imported_physician_text_files.iloc[:,[2,3,5,6,4,16,17]]

    # Creating a column that stores state abbreviation from file name. Also extracting file name from directory file path
    imported_physician_text_files['STATE'] = os.path.basename(file_path)

    # Remove extension from file name
    imported_physician_text_files['STATE'] = pathlib.Path(file_path).stem

    # Extract State from file name
    imported_physician_text_files['STATE'] = imported_physician_text_files['STATE'].str[2:4]
    return imported_physician_text_files

# Get the current script's directory
current_directory = os.getcwd()
physician_folder = os.path.join(current_directory, "Program Data", "Physician")

# Getting the filenames of all text files in the Physician folder
physician_file_directory = glob.glob(os.path.join(physician_folder, "*.txt"))

# Import all text files and concatenate data into a dataframe
physician_cptrates_df = pd.concat((processor_text_physicians(text_file) for text_file in physician_file_directory))

# Get the today's year
year = datetime.datetime.now().year

# Formulate the output CSV filename with the current year
output_filename = os.path.join("Program Data", f"physician_cptrates_{year}.csv")

# Export physicians CPT rates dataframe into a CSV output file
physician_cptrates_df.to_csv(output_filename, index=False)

print('Initiating Data Processing: Loading DME File...')

# Specify the relative path to the Program Data/DME folder
dme_folder = os.path.join(current_directory, "Program Data", "DME")

# Import CSV DME file, skip the first 6 rows
dme_file_path = os.path.join(dme_folder, "DMEPOS_Jan.xlsx")
imported_dme_file = pd.read_excel(dme_file_path, skiprows=6)

# Remove unnecessary columns, ignoring columns listed that in the ticket description. Also moves MOD1 column positiion to the beginning of USA columns
imported_dme_file = imported_dme_file.drop(['JURIS', 'CATG', 'Ceiling', 'Floor', 'Description'], axis = 1)

# Create variable with R (Rural) columns to be replaced with blank values
columns_with_rural = imported_dme_file.columns[imported_dme_file.columns.str.endswith('(R)')]

# Drop columns states with rural to focus only on states with (NR) Non-rural columns
imported_dme_file.drop(columns_with_rural, axis = 1, inplace = True)

# Create dictionary to update dataframe headers
imported_dme_file_dictionary = {'HCPCS': 'CPT', 'Mod': 'MOD1', 'Mod2': 'MOD2'}

# Rename dataframe headers with updated headers
imported_dme_file.rename(columns = imported_dme_file_dictionary, inplace = True)

# Added USA columns such as MOD1 and MOD2 filled with null values (NaN)
imported_dme_file[['MOD1', 'MOD2']] = imported_dme_file[['MOD1', 'MOD2']].replace(r'^\s*$', np.nan, regex=True)

# Transpose and melt existing columns, keeping CPT, MOD1, MOD2 constant columns, create new variable for state, rename values to rates
dme_cptrates_df = pd.melt(imported_dme_file, id_vars = ['CPT', 'MOD1', 'MOD2'], var_name = 'STATE', value_name = 'RATES')

# Replace (NR) strings with blank values to only have state
dme_cptrates_df['STATE'] = dme_cptrates_df['STATE'].str.replace("(NR)", "")

# Remove leading and trailing space of the state column
dme_cptrates_df['STATE'] = dme_cptrates_df['STATE'].str.strip()

# Filter rows that valid rates into the same data frame
cleaned_dme_cptrates_df = dme_cptrates_df[pd.to_numeric(dme_cptrates_df['RATES'], errors = 'coerce').notnull()].copy()

# Filter rows that have errors (such as strings, any non-integer or non-numeric values) into a new data frame for error checking
errors_dme_cptrates_df = dme_cptrates_df[pd.to_numeric(dme_cptrates_df['RATES'], errors = 'coerce').isnull()].copy()

# This code will also change data type of RATES column to a float value
cleaned_dme_cptrates_df['RATES'] = cleaned_dme_cptrates_df['RATES'].astype(float)

# Drop rows based on rates, specifically RATES when RATES = 0.00
nonzero_dme_cptrates_df = cleaned_dme_cptrates_df[cleaned_dme_cptrates_df['RATES'] != 0.00].copy()

# Change the order of dataframe columns, inserting state at the beginning of the dataframe
processed_dme_cptrates_df = nonzero_dme_cptrates_df.iloc[:,[3,0,1,2,4]].copy()

# Formulate the output CSV filenames with the current year
output_dme_cptrates_filename = os.path.join("Program Data", f"dme_cptrates_{year}.csv")
output_errors_dme_cptrates_filename = os.path.join("Program Data", f"errors_dme_cptrates_{year}.csv")

# Export DME CPT rates dataframe into a CSV output file
processed_dme_cptrates_df.to_csv(output_dme_cptrates_filename, index=False)

# Export DME CPT error rates dataframe into a CSV output file
errors_dme_cptrates_df.to_csv(output_errors_dme_cptrates_filename, index=False)

print('Initiating Data Processing: Loading Injectables File...')

# Specify the relative path to the Program Data/DME folder
injectables_folder = os.path.join(current_directory, "Program Data", "Injectable")

# Import CSV DME file, skip the first 6 rows
injectables_file_path = os.path.join(injectables_folder, "January 2024 ASP Pricing File 122023.xls")

# Import Excel injectables file, skip the first 8 rows
imported_injectables_file = pd.read_excel(injectables_file_path,
                                          names=['HCPCS Code', 'Short Description', 'HCPCS Code Dosage', 'Payment Limit',
                                                 'Co-insurance Percentage', 'Vaccine AWP%', 'Vaccine Limit', 'Blood AWP%',
                                                 'Blood limit', 'Clotting Factor', 'Notes'],
                                          skiprows=8)

# Remove unnecessary columns, ignoring columns listed that in the ticket description
imported_injectables_file = imported_injectables_file.drop(['Short Description', 'HCPCS Code Dosage', 'Co-insurance Percentage', 'Vaccine AWP%', 'Vaccine Limit', 
                                                            'Blood AWP%', 'Blood limit', 'Clotting Factor', 'Notes'], axis = 1)

# Create dictionary to update dataframe headers
imported_injectables_file_dict = {'HCPCS Code': 'CPT', 'Payment Limit': 'RATES'}

# Rename dataframe headers with updated headers
imported_injectables_file.rename(columns = imported_injectables_file_dict, inplace = True)

# Added USA columns such as MOD1 and MOD2 with null values (NaN)
imported_injectables_file[['MOD1', 'MOD2']] = np.nan

# Filter rows that valid rates into the same data frame
cleaned_injectables_file = imported_injectables_file[pd.to_numeric(imported_injectables_file['RATES'], errors='coerce').notnull()].copy()

# Filter rows that have errors (such as strings, any non-integer or non-numeric values) into a new data frame for error checking
errors_injectables_cptrates_df = imported_injectables_file[pd.to_numeric(imported_injectables_file['RATES'], errors='coerce').isnull()].copy()

# This code will also change data type of RATES column to a float value
cleaned_injectables_file['RATES'] = cleaned_injectables_file['RATES'].astype(float)

# Replace blank spaces with zeroes for column RATES
cleaned_injectables_file['RATES'] = cleaned_injectables_file['RATES'].replace('', 0)

# Drop rows based on rates, specifically RATES when RATES = 0.00
nonzero_injectables_file = cleaned_injectables_file[cleaned_injectables_file['RATES'] != 0.00].copy()

# Change the order of dataframe columns, inserting state at the beginning of the dataframe
processed_injectables_file = nonzero_injectables_file.iloc[:,[0,2,3,1]].copy()

# Formulate the output CSV filenames with the current year
output_injectables_cptrates_filename = os.path.join("Program Data", f"injectables_cptrates_{year}.csv")
output_errors_injectables_cptrates_filename = os.path.join("Program Data", f"errors_injectables_cptrates_{year}.csv")

# Export Injectables CPT rates dataframe into a CSV output file
processed_injectables_file.to_csv(output_injectables_cptrates_filename, index=False)

# Export Injectables CPT error rates dataframe into a CSV output file
errors_injectables_cptrates_df.to_csv(output_errors_injectables_cptrates_filename, index=False)

print('Data Processing: Complete')

# Add a pause command to keep the terminal open
input('\nPress Enter to exit the program')