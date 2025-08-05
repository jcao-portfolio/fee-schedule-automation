# Introduction to the fee schedule program (welcome page for users)
welcome_message = """
--------------------------------------------------------------
           Fee Schedule Automation Program Part Two
--------------------------------------------------------------
Loading files... Estimated load time: 1 minute
"""
print(welcome_message)

# Import packages & libraries for data cleaning and processing
import pandas as pd
import numpy as np
import datetime

# Get the today's year
year = datetime.datetime.now().year

# Import pre-processed data from part one
physician_cptrates_df = pd.read_csv(f'Program Data/physician_cptrates_{year}.csv')
processed_dme_cptrates_df = pd.read_csv(f'Program Data/dme_cptrates_{year}.csv')
processed_injectables_file = pd.read_csv(f'Program Data/injectables_cptrates_{year}.csv')

# Allowing user input to filter dataframe by state abbbreviation (upper used to convert to uppercase for case-insensitivity), locality number, percentage, rate type, fee schedule number
state = input('Enter state abbreviation to filter Physician & DME file (ex. AZ, VA, CA): ').upper()

# Filter rows by state abbreviation and locality number
physicians_cptrates_filtered_by_state = physician_cptrates_df[physician_cptrates_df['STATE'] == state]

unique_localities = sorted(physicians_cptrates_filtered_by_state['LOCALITY'].unique())
print('Localities for ' + state + ': ' + str(unique_localities))

# User input for locality with validation
while True:
    try:
        locality = int(input('\nEnter locality number to filter Physician file: '))
        if locality not in unique_localities:
            raise ValueError('Invalid locality, please try again and enter a locality from the list.')
        break
    except ValueError as ve:
        print(ve)

# Filters table
physicians_cptrates_filtered = physicians_cptrates_filtered_by_state[physicians_cptrates_filtered_by_state['LOCALITY'] == locality]

fee_schedule_percentage = int(input('Enter fee schedule percentage (ex. 100, 110, 120): '))
rate_type = int(input('Enter numeric value to choose between Physician = (1) or Facility = (2): '))
fee_schedule_number = input('Enter fee schedule number (ex. 1234, 6775): ')
print('')

# User input response/feedback about state abbreviation, locality number, percentage, number, rate type, fee schedule number
print('State abbreviation entered: ' + state)
print(f'Locality number entered: {locality:02d}')
print(f'Fee schedule percentage entered: {fee_schedule_percentage}%')
print('Fee schedule number entered: ' + fee_schedule_number)

# Applying if-else statement to choose between Physicians and Facility, drop physician/facility CPT rates column depending on user input, while also renaming selected column
# If user chooses rate type = Physician:
if rate_type == 1:
    # Drop Facility rates column and rename Physician Rates to Rates
    physicians_cptrates_filtered = physicians_cptrates_filtered.drop(columns = 'FACILITY-RATES')
    processed_physicians_cptrates_df = physicians_cptrates_filtered.rename(columns = {'PHYSICIANS-RATES': 'RATES'})
    print('Rate type entered: Physician CPT Rates\n')
# If user chooses rate type = Facility:
elif rate_type == 2:
    # Drop Physician rates column and rename Facility Rates to Rates
    physicians_cptrates_filtered = physicians_cptrates_filtered.drop(columns = 'PHYSICIANS-RATES')
    processed_physicians_cptrates_df = physicians_cptrates_filtered.rename(columns = {'FACILITY-RATES': 'RATES'})
    print('Rate type entered: Facility CPT Rates\n')
# Invalid response prompt incase there are any errors or mistakes in user input
else:
    print('Invalid selection. Please enter a valid numeric value (1 or 2).')

# Change the order of dataframe columns, as well as dropping unnecessary columns
processed_physicians_cptrates_file = processed_physicians_cptrates_df.iloc[:,[1,3,4,2]].copy()

# Filter rows by state abbreviation and locality number
processed_dme_cptrates_file = processed_dme_cptrates_df[(processed_dme_cptrates_df['STATE'] == state)]

# Change the order of dataframe columns
processed_dme_cptrates_file = processed_dme_cptrates_file.iloc[:,[1,2,3,4]].copy()

# Combine/concatenate Physicians, DME, and Injectable file into one dataframe (generated fee schedule)
processed_fee_schedule_combined = pd.concat([processed_physicians_cptrates_file, processed_dme_cptrates_file, processed_injectables_file])

# Add MOD3 and MOD4 to the final combined dataframe with null values (NaN)
processed_fee_schedule_combined[['MOD3', 'MOD4']] = np.nan

# Applying if-else statement when a fee schedule percentage is entered, creates a new column, multiply all rows in RATES column and move new records into new column, dropping the non-calculated rates column
default_percentage = 100
# If user inputs fee schedule percentage as 100% (default)
if fee_schedule_percentage == default_percentage:
    # Round 'RATES' column by six decimal points
    processed_fee_schedule_combined['RATES'] = processed_fee_schedule_combined['RATES'].round(6)
    processed_fee_schedule_final = processed_fee_schedule_combined.iloc[:,[0,1,2,4,5,3]]
# If user inputs fee schedule percentage other than 100%
elif fee_schedule_percentage != default_percentage:
    # If fee schedule percentage entered is not 100, it will go through this program, which will multiply all rates by the percentage and create a new column for the calculated rates
    processed_fee_schedule_combined['FS_PERCENT'] = fee_schedule_percentage / 100
    processed_fee_schedule_combined['CALCULATED_RATES'] = processed_fee_schedule_combined['RATES'] * processed_fee_schedule_combined['FS_PERCENT']
    # Round 'CALCULATED_RATES' column by six decimal points
    processed_fee_schedule_combined['CALCULATED_RATES'] = processed_fee_schedule_combined['CALCULATED_RATES'].round(6)
    processed_fee_schedule_combined.rename(columns = {'CALCULATED_RATES': 'RATES'}, inplace = True)
    processed_fee_schedule_final = processed_fee_schedule_combined.iloc[:,[0,1,2,4,5,7]]
else:
    pass

# Print status when fee schedule is successfully generated, as well as today's date
separator = '-' * 50
print(separator)
today = datetime.date.today()
formatted_today_date = today.strftime("%m-%d-%Y")
print(f'Fee Schedule successfully generated on ' + formatted_today_date)
separator = '-' * 50
print(separator)

# Output Fee Schedule as CSV file
# Get the year of the date in a variable
year = today.strftime("%Y")

# Store csv output file path into its own variable
csv_output_file = 'Fee Schedule Output/FS_' + fee_schedule_number + '_' + state + '_' + (format(locality, '02d')) + '_' + str(fee_schedule_percentage) + 'perc' + '_' + year + '.csv'

# Print the file path and notify user where it is located
print('Fee schedule for FS_' + fee_schedule_number + ' has been successfully processed and generated. You can find it here:', csv_output_file)

# Output processed fee schedule into a CSV file
processed_fee_schedule_final.to_csv(csv_output_file, index = False, header = True)

# Add a pause command to keep the terminal open
input('\nPress Enter to exit the program')