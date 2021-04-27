#from IPython.core.display import display

# basic stuff
import os
import json

# data science stuff
import pandas as pd

# import the modules to wrangle the data
# import baselineAIS
# import extendAIS
import report_output
import financial_output

settingsfile = "projectsettings.json"
# Read settings from json file
with open(settingsfile, 'r') as jsonf:
    SETTINGS = json.load(jsonf)

retrieval_set_name = SETTINGS['filenames']["retrieval_set_name"]
ref_in_fname = SETTINGS['filenames']["ref_in_fname"]  # used as reference in output filename

startdate = SETTINGS['dates']["startdate"]
enddate = SETTINGS['dates']["enddate"]
# enddate="2020-9-1"


# Save statistics data, needed for SFTP
yearfolder = SETTINGS['output']["yearfolder"]
municipality = SETTINGS['output']["municipality"]

# timedelta to check if same session
# the maximum time between 2 registrations to be seen as one session
session_border = SETTINGS['calculations']["session_border_in_hours"]

# OTHER PARAMETERS
###################

# folders for output
ref_dir = SETTINGS['folders']["ref_dir"]

# folders for output
output_dir = SETTINGS['folders']["output_dir"]
output_tmp = SETTINGS['folders']["output_tmp"]

# folder for settings
settings_dir = SETTINGS['folders']["settings_dir"]

# path_to_files="/home/developer/myPolygons/"
# path_to_files="C:/Users/pierr_8jj0nf8/OneDrive/@pvln_coding_PVE/myPolygons/"
path_to_files = "C:/Users/developer/OneDrive/@pvln_coding_PVE/myPolygons/"
# path_to_files = "C:/Users/pierre/OneDrive/@pvln_coding_PVE/myPolygons/"

output_to_excel = SETTINGS['output']["output_to_excel"]

# https://support.microsoft.com/en-us/office/excel-specifications-and-limits-1672b34d-7043-467e-8e27-269d656771c3
max_excel_lines = SETTINGS['output']["max_excel_lines"]

# debugging
full_verbose = SETTINGS['debug']["full_verbose"]

# what to do with output files; reread them?
# reread_csv = SETTINGS['output']["output_to_excel"] #False levert mog problemen op

# check if output folder exists. If not create it.
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# check if temp output folder exists. If not create it.
if not os.path.exists(output_tmp):
    os.makedirs(output_tmp)

####################################
#
# BSGW OUTPUT
#
####################################

#
#  (re)load the data (always csv), as exel might not contain all data or is not present at all
#
input_filename = output_dir+ref_in_fname+"_"+retrieval_set_name+"_statistics_output"
BSGW_output = pd.read_csv(input_filename+".csv", index_col=0, dtype=str)
# BSGW_output = statistics_output.reset_index(drop=True)
BSGW_output = BSGW_output.reset_index(drop=True)
if full_verbose:
    print(BSGW_output.dtypes)

# keep only quay rows 
indexList = BSGW_output[(BSGW_output['location_type'] != 'quay')].index

# Delete these row indexes from dataFrame
BSGW_output.drop(indexList, inplace=True)

if full_verbose:
    print(BSGW_output.shape)
    print(BSGW_output)

BSGW_output = financial_output.add_billing_info(inputdf=BSGW_output,
                                                reference_dir=ref_dir,
                                                reference_filename="billing_info.xlsx",
                                                verbose=True)

df_missing_billing = report_output.missing_info(inputdf=BSGW_output,
                                                check_column='factuur naam',
                                                verbose=True)

output_filename = output_dir+ref_in_fname+"_"+retrieval_set_name+"_BSGW_output_TEMP"
# extended data output files
BSGW_output.to_csv(output_filename+".csv")
if output_to_excel and len(BSGW_output.index) < max_excel_lines: 
    BSGW_output.to_excel(output_filename+".xlsx", index=False)

output_filename = output_dir+ref_in_fname+"_"+retrieval_set_name+"_missing_billing_info"
# extended data output files
df_missing_billing.to_csv(output_filename+".csv")
if output_to_excel and len(df_missing_billing.index) < max_excel_lines: 
    df_missing_billing.to_excel(output_filename+".xlsx", index=False)

if full_verbose:
    print(BSGW_output.dtypes)


# Set specific columns
'''
# BSGW_output['local_time_min']=BSGW_output['local_time_min'].apply(str)
# BSGW_output['local_time_max']=BSGW_output['local_time_max'].apply(str)

# Only date is needed not time
print("1 ============================")
print(BSGW_output['local_time_min'])
print("============================")

#BSGW_output['local_time_min'] = BSGW_output['local_time_min'].dt.strftime('%Y-%m-%d')
'''
print("1 ============================")
print(BSGW_output['local_time_min'])

#BSGW_output['local_time_min'] = BSGW_output['local_time_min'].strftime('%Y-%m-%d')
BSGW_output['local_time_min'] = pd.to_datetime(BSGW_output['local_time_min'])
BSGW_output['local_time_min'] = BSGW_output['local_time_min'].dt.strftime('%Y-%m-%d')

#print("2 ============================")
#print(BSGW_output['local_time_min'])

'''
print("2 ============================")
print(BSGW_output['local_time_min'])
print("============================")

print("3 ============================")
print(BSGW_output['local_time_max'])
print("============================")


#BSGW_output['local_time_max'] = BSGW_output['local_time_max'].dt.strftime('%Y-%m-%d')
'''
BSGW_output['local_time_max'] = pd.to_datetime(BSGW_output['local_time_max'])
BSGW_output['local_time_max'] = BSGW_output['local_time_max'].dt.strftime('%Y-%m-%d')
'''
print("4 ============================")
print(BSGW_output['local_time_max'])
print("============================")
'''

BSGW_output['Naam'] = BSGW_output['factuur naam']

BSGW_output['Subjectsoort'] = "R"
BSGW_output.loc[BSGW_output["Landnaam"] != "", 'Subjectsoort'] = "E"

BSGW_output['GEM. HEFSOORT'] = "NHAV"

BSGW_output['Subjectnr. ext'] = BSGW_output['tonnage']

# de tekens: € / \ " ? ~ ` zijn niet toegestaan 
# maximale lengte 60 chars
BSGW_output['Omschrijving 1'] = BSGW_output['location_name'] + " / " + BSGW_output['name'] + " [" + BSGW_output['registratie-land'].str.replace(" ", "") + "]" + " /ENI: " + BSGW_output['eni'] + " /Tonn: " + BSGW_output['tonnage']
BSGW_output['Omschrijving 1'] = BSGW_output['Omschrijving 1'].str.replace("€", "Euro")
BSGW_output['Omschrijving 1'] = BSGW_output['Omschrijving 1'].str.replace("/", '-')
BSGW_output['Omschrijving 1'] = BSGW_output['Omschrijving 1'].str.replace("\\", '-')
BSGW_output['Omschrijving 1'] = BSGW_output['Omschrijving 1'].str.replace('"', '')
BSGW_output['Omschrijving 1'] = BSGW_output['Omschrijving 1'].str.replace("?", '.')
BSGW_output['Omschrijving 1'] = BSGW_output['Omschrijving 1'].str.replace("~", '-')
BSGW_output['Omschrijving 1'] = BSGW_output['Omschrijving 1'].str.replace("`", '-')
BSGW_output['Omschrijving 1'] = BSGW_output['Omschrijving 1'].str.replace("Kade ", '')
BSGW_output['Omschrijving 1'] = BSGW_output['Omschrijving 1'].str.replace(" Born", '')
BSGW_output['Omschrijving 1'] = BSGW_output['Omschrijving 1'].str[0:58]

BSGW_output['Omschrijving 2'] = "van " + BSGW_output['local_time_min'] + " tot " + BSGW_output['local_time_max']
BSGW_output['Omschrijving 2'] = BSGW_output['Omschrijving 2'].str.replace("€", 'Euro')
BSGW_output['Omschrijving 2'] = BSGW_output['Omschrijving 2'].str.replace("/", '-')
BSGW_output['Omschrijving 2'] = BSGW_output['Omschrijving 2'].str.replace("\\", '-')
BSGW_output['Omschrijving 2'] = BSGW_output['Omschrijving 2'].str.replace('"', '')
BSGW_output['Omschrijving 2'] = BSGW_output['Omschrijving 2'].str.replace("?", '.')
BSGW_output['Omschrijving 2'] = BSGW_output['Omschrijving 2'].str.replace("~", '-')
BSGW_output['Omschrijving 2'] = BSGW_output['Omschrijving 2'].str.replace("`", '-')
BSGW_output['Omschrijving 2'] = BSGW_output['Omschrijving 2'].str[0:58]

BSGW_output['Omschrijving 3'] = ""

BSGW_output['Verblijfsduur'] = BSGW_output['time_diff_str']
BSGW_output['Verblijfsduur'] = BSGW_output['Verblijfsduur'].str.replace("0 days", '')
BSGW_output['Verblijfsduur'] = BSGW_output['Verblijfsduur'].str.replace("1 days", '1 dag')
BSGW_output['Verblijfsduur'] = BSGW_output['Verblijfsduur'].str.replace("days", 'dagen')
BSGW_output['Verblijfsduur'] = BSGW_output['Verblijfsduur'].str.replace("€", 'Euro')
BSGW_output['Verblijfsduur'] = BSGW_output['Verblijfsduur'].str.replace("/", '-')
BSGW_output['Verblijfsduur'] = BSGW_output['Verblijfsduur'].str.replace("\\", '-')
BSGW_output['Verblijfsduur'] = BSGW_output['Verblijfsduur'].str.replace('"', '')
BSGW_output['Verblijfsduur'] = BSGW_output['Verblijfsduur'].str.replace("?", '.')
BSGW_output['Verblijfsduur'] = BSGW_output['Verblijfsduur'].str.replace("~", '-')
BSGW_output['Verblijfsduur'] = BSGW_output['Verblijfsduur'].str.replace("`", '-')
BSGW_output['Verblijfsduur'] = BSGW_output['Verblijfsduur'].str[0:58]

BSGW_output['MMSI-info'] = BSGW_output['mmsi']

current_columns = list(BSGW_output.columns)

# CREATE OUTPUT
columns_to_write = ['Naam', 'Voorletters', 'Voorvoegsel', 'Voornaam', 'Geslacht',
                    'Burgersservicenr.', 'A-nummer', 'Handels - KVK-nr', 'Subjectsoort',
                    'Geboortedatum', 'Banknr', 'Gironummer', 'Soort Adres', 'Datum Ingang Adres',
                    'datum Einde Adres', 'Straat', 'Huisnr.', 'Postcode numeriek', 'Postcode alfanumeriek',
                    'Postbusnr.', 'Huisletter', 'Toevoeging huisnr.', 'Aanduiding', 'Woonplaats', 'Buit. Adres 1',
                    'Buit. Adres 2', 'Buit. Adres 3', 'Buit. Adres 4', 'Landnaam', 'Datum Overlijden',
                    'BSN/Sofinr. Extra', 'Iban.rek.nr.', 'Bic-code', 'Subjectnr. ext', 'Vorderingnr.',
                    'Heffingsjaar', 'Dagtekening', 'Bedrag incl.BTW', 'GEM. HEFSOORT', 'Bedrag excl.BTW',
                    'Bedrag BTW', 'Omschrijving 1', 'Omschrijving 2', 'Omschrijving 3', 'LEEG', 'Verblijfsduur', 'MMSI-info']

# ADD MISSING COLUMNS
columns_to_add = set(list(columns_to_write))-set(list(current_columns))
BSGW_output = pd.concat([BSGW_output, pd.DataFrame(columns=columns_to_add)], sort=False)

# Sort on Omschrijving1, Omschrijving3 columns

BSGW_output.sort_values(['Omschrijving 1', 'Omschrijving 2'], ascending=[True, True], inplace=True)

output_filename = output_dir+ref_in_fname+"_"+retrieval_set_name+"_BSGW_output"
# extended data output files
BSGW_output.to_csv(output_filename+".csv", columns=columns_to_write, index=False)
if output_to_excel and len(df_missing_billing.index) < max_excel_lines: 
    BSGW_output.to_excel(output_filename+".xlsx", columns=columns_to_write, index=False)
