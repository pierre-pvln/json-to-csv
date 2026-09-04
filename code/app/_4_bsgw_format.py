# basic stuff
import os
import json
import socket

# data science stuff
import pandas as pd

# aws stuff
import boto3
import awswrangler as wr

# import the modules to wrangle the data
import report_output
import financial_output

settingsfile = "projectsettings.json"
# Read settings from json file
with open(settingsfile, 'r') as jsonf:
    SETTINGS = json.load(jsonf)

ref_in_filename = SETTINGS['filenames']["ref_in_fname"]  # used as reference in output filename

projectname = SETTINGS['project']['name']
folderprefix = SETTINGS['project']['folderprefix']

output_bucket = SETTINGS['s3']['outputbucket']

# folders for output
ref_dir = SETTINGS['folders']["ref_dir"]

# folders for output
output_dir = SETTINGS['folders']["output_dir"]
output_tmp = SETTINGS['folders']["output_tmp"]

output_to_excel = SETTINGS['output']["output_to_excel"]

# https://support.microsoft.com/en-us/office/excel-specifications-and-limits-1672b34d-7043-467e-8e27-269d656771c3
max_excel_lines = SETTINGS['output']["max_excel_lines"]

# debugging
full_verbose = SETTINGS['debug']["full_verbose"]

the_hostname = socket.gethostname()
print('running on   : '+the_hostname)

if the_hostname != 'ip-10-0-1-5':
    # were probably running local so we need credentials
    # get settings for aws profile from environment variables
    profile_name = os.environ.get("AWS_PROFILE_NAME")
    boto3.setup_default_session(profile_name=os.environ.get("AWS_PROFILE_NAME"))
    print("profile_name : "+profile_name)

_S3_CLIENT = boto3.client("s3")

####################################
# BSGW OUTPUT
####################################

#
#  (re)load the data (always csv), as exel might not contain all data or is not present at all
#
input_filename = output_dir + ref_in_filename + "_" + the_hostname + "_" + projectname + "_statistics_output"
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

if len(BSGW_output) > 0:
    # save the df to s3
    wr.s3.to_csv(df=BSGW_output,
                 index=False,
                 path='s3://' + output_bucket + "/" + folderprefix + "/" + ref_in_filename + "/details/" + the_hostname + "_" + projectname + "_BSGW_output_TEMP.csv"
                 )
# check if not running as Lambda function
# https://stackoverflow.com/questions/36287374/how-to-check-if-python-app-is-running-within-aws-lambda-function
#
if os.environ.get("AWS_EXECUTION_ENV") is None:
    # save df also to local disk for further processing

    # check if output folder exists. If not create it.
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_filename = output_dir + ref_in_filename + "_" + the_hostname + "_" + projectname + "_BSGW_output_TEMP"
    # extended data output files
    BSGW_output.to_csv(output_filename+".csv")
    if output_to_excel and len(BSGW_output.index) < max_excel_lines:
        BSGW_output.to_excel(output_filename+".xlsx", index=False)

filekey = folderprefix + "/" + ref_in_filename + "/details/" + the_hostname + "_" + projectname + "_missing_billing_info"
s3_path = 's3://' + output_bucket + "/" + filekey
if len(df_missing_billing) > 0:
    # save the df to s3
    wr.s3.to_csv(df=df_missing_billing, index=False, path=s3_path + ".csv")
    if output_to_excel and len(df_missing_billing.index) < max_excel_lines:
        wr.s3.to_excel(df=df_missing_billing, index=False, path=s3_path + ".xlsx")
else:
    print("TODO: Should check if missing_ships_info file exists and if so remove it")

    response = _S3_CLIENT.list_objects_v2(Bucket=output_bucket, Prefix=filekey+".csv")
    for obj in response.get('Contents', []):
        print("=====")
        print(obj)
        print("=====")
        if obj['Key'] == filekey+".csv":
            print(obj)
            print("Should now delete object")
            _S3_CLIENT.delete_object(Bucket=output_bucket, Key=filekey + ".csv")

    response = _S3_CLIENT.list_objects_v2(Bucket=output_bucket, Prefix=filekey+".xlsx")
    for obj in response.get('Contents', []):
        print("=====")
        print(obj)
        print("=====")
        if obj['Key'] == filekey+".xlsx":
            print(obj)
            print("Should now delete object")
            _S3_CLIENT.delete_object(Bucket=output_bucket, Key=filekey + ".xlsx")
# OLD #
# if len(df_missing_billing) > 0:
#     # save the df to s3
#     wr.s3.to_csv(df=df_missing_billing,
#                  index=False,
#                  path='s3://' + output_bucket + "/" + folderprefix + "/" + ref_in_filename + "/details/" + the_hostname + "_" + projectname + "_missing_billing_info.csv"
#                  )

output_filename = output_dir + ref_in_filename + "/" + the_hostname + "_" + projectname + "_missing_billing_info"
# check if not running as Lambda function
# https://stackoverflow.com/questions/36287374/how-to-check-if-python-app-is-running-within-aws-lambda-function
#
if os.environ.get("AWS_EXECUTION_ENV") is None:
    # save df also to local disk for further processing

    # check if output folder exists. If not create it.
    if not os.path.exists(output_dir + ref_in_filename):
        os.makedirs(output_dir + ref_in_filename)

    if len(df_missing_billing) > 0:
        # extended data output files
        df_missing_billing.to_csv(output_filename+".csv", index=False)
        if output_to_excel and len(df_missing_billing.index) < max_excel_lines:
            df_missing_billing.to_excel(output_filename+".xlsx", index=False)
    else:
        print("Removing files if they exist", output_filename)
        if os.path.exists(output_filename+".csv"):
            os.remove(output_filename+".csv")
        if os.path.exists(output_filename+".xlsx"):
            os.remove(output_filename+".xlsx")

# if os.environ.get("AWS_EXECUTION_ENV") is None:
#     # save df also to local disk for further processing
#
#     # check if output folder exists. If not create it.
#     if not os.path.exists(output_dir):
#         os.makedirs(output_dir)
#
#     output_filename = output_dir + ref_in_filename + "_" + the_hostname + "_" + projectname + "_missing_billing_info"
#     # extended data output files
#     df_missing_billing.to_csv(output_filename + ".csv")
#     if output_to_excel and len(df_missing_billing.index) < max_excel_lines:
#         df_missing_billing.to_excel(output_filename + ".xlsx", index=False)

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

# BSGW_output['local_time_min'] = BSGW_output['local_time_min'].strftime('%Y-%m-%d')
BSGW_output['local_time_min'] = pd.to_datetime(BSGW_output['local_time_min'])
BSGW_output['local_time_min'] = BSGW_output['local_time_min'].dt.strftime('%Y-%m-%d')

# print("2 ============================")
# print(BSGW_output['local_time_min'])

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
BSGW_output['Omschrijving 1'] = BSGW_output['location_name'] + " / " + BSGW_output['name'] + " [" + BSGW_output['registratie-land'].str.replace(" ", "", regex=False) + "]" + " /ENI: " + BSGW_output['eni'] + " /Tonn: " + BSGW_output['tonnage']
BSGW_output['Omschrijving 1'] = BSGW_output['Omschrijving 1'].str.replace("€", "Euro", regex=False)
BSGW_output['Omschrijving 1'] = BSGW_output['Omschrijving 1'].str.replace("/", '-', regex=False)
BSGW_output['Omschrijving 1'] = BSGW_output['Omschrijving 1'].str.replace("\\", '-', regex=False)
BSGW_output['Omschrijving 1'] = BSGW_output['Omschrijving 1'].str.replace('"', '', regex=False)
BSGW_output['Omschrijving 1'] = BSGW_output['Omschrijving 1'].str.replace("?", '.', regex=False)
BSGW_output['Omschrijving 1'] = BSGW_output['Omschrijving 1'].str.replace("~", '-', regex=False)
BSGW_output['Omschrijving 1'] = BSGW_output['Omschrijving 1'].str.replace("`", '-', regex=False)
BSGW_output['Omschrijving 1'] = BSGW_output['Omschrijving 1'].str.replace("Kade ", '', regex=False)
BSGW_output['Omschrijving 1'] = BSGW_output['Omschrijving 1'].str.replace(" Born", '', regex=False)
BSGW_output['Omschrijving 1'] = BSGW_output['Omschrijving 1'].str[0:58]

BSGW_output['Omschrijving 2'] = "van " + BSGW_output['local_time_min'] + " tot " + BSGW_output['local_time_max']
BSGW_output['Omschrijving 2'] = BSGW_output['Omschrijving 2'].str.replace("€", 'Euro', regex=False)
BSGW_output['Omschrijving 2'] = BSGW_output['Omschrijving 2'].str.replace("/", '-', regex=False)
BSGW_output['Omschrijving 2'] = BSGW_output['Omschrijving 2'].str.replace("\\", '-', regex=False)
BSGW_output['Omschrijving 2'] = BSGW_output['Omschrijving 2'].str.replace('"', '', regex=False)
BSGW_output['Omschrijving 2'] = BSGW_output['Omschrijving 2'].str.replace("?", '.', regex=False)
BSGW_output['Omschrijving 2'] = BSGW_output['Omschrijving 2'].str.replace("~", '-', regex=False)
BSGW_output['Omschrijving 2'] = BSGW_output['Omschrijving 2'].str.replace("`", '-', regex=False)
BSGW_output['Omschrijving 2'] = BSGW_output['Omschrijving 2'].str[0:58]

BSGW_output['Omschrijving 3'] = ""

BSGW_output['Verblijfsduur'] = BSGW_output['time_diff_str']
BSGW_output['Verblijfsduur'] = BSGW_output['Verblijfsduur'].str.replace("0 days", '', regex=False)
BSGW_output['Verblijfsduur'] = BSGW_output['Verblijfsduur'].str.replace("1 days", '1 dag', regex=False)
BSGW_output['Verblijfsduur'] = BSGW_output['Verblijfsduur'].str.replace("days", 'dagen', regex=False)
BSGW_output['Verblijfsduur'] = BSGW_output['Verblijfsduur'].str.replace("€", 'Euro', regex=False)
BSGW_output['Verblijfsduur'] = BSGW_output['Verblijfsduur'].str.replace("/", '-', regex=False)
BSGW_output['Verblijfsduur'] = BSGW_output['Verblijfsduur'].str.replace("\\", '-', regex=False)
BSGW_output['Verblijfsduur'] = BSGW_output['Verblijfsduur'].str.replace('"', '', regex=False)
BSGW_output['Verblijfsduur'] = BSGW_output['Verblijfsduur'].str.replace("?", '.', regex=False)
BSGW_output['Verblijfsduur'] = BSGW_output['Verblijfsduur'].str.replace("~", '-', regex=False)
BSGW_output['Verblijfsduur'] = BSGW_output['Verblijfsduur'].str.replace("`", '-', regex=False)
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
columns_to_add = list(set(list(columns_to_write))-set(list(current_columns)))
BSGW_output = pd.concat([BSGW_output, pd.DataFrame(columns=columns_to_add)], sort=False)

# Sort on Omschrijving1, Omschrijving2 columns

BSGW_output.sort_values(['Omschrijving 1', 'Omschrijving 2'], ascending=[True, True], inplace=True)

if len(BSGW_output) > 0:
    # save the df to s3 in csv and xslx format
    wr.s3.to_csv(df=BSGW_output,
                 columns=columns_to_write,
                 index=False,
                 path='s3://' + output_bucket + "/" + folderprefix + "/" + ref_in_filename + "/" + ref_in_filename + "_" + the_hostname + "_" + projectname + "_BSGW_output.csv")

    wr.s3.to_excel(df=BSGW_output,
                   columns=columns_to_write,
                   index=False,
                   path='s3://' + output_bucket + "/" + folderprefix + "/" + ref_in_filename + "/" + ref_in_filename + "_" + the_hostname + "_" + projectname + "_BSGW_output.xlsx")

# check if not running as Lambda function
# https://stackoverflow.com/questions/36287374/how-to-check-if-python-app-is-running-within-aws-lambda-function
#
if os.environ.get("AWS_EXECUTION_ENV") is None:
    # save df also to local disk for further processing

    # check if output folder exists. If not create it.
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_filename = output_dir + ref_in_filename + "_" + the_hostname + "_" + projectname + "_BSGW_output"
    # extended data output files
    BSGW_output.to_csv(output_filename + ".csv", columns=columns_to_write, index=False)
    if output_to_excel and len(df_missing_billing.index) < max_excel_lines:
        BSGW_output.to_excel(output_filename + ".xlsx", columns=columns_to_write, index=False)
