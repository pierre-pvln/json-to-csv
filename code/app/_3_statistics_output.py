# basic stuff
import os
import json
import socket
# import getpass

# data science stuff
import pandas as pd

# aws stuff
import boto3
import awswrangler as wr

# import the modules to wrangle the data
# import baselineAIS
# import extendAIS
import report_output
# import financial_output

settingsfile = "projectsettings.json"
# Read settings from json file
with open(settingsfile, 'r') as jsonf:
    SETTINGS = json.load(jsonf)

# TODO verwidjeren
# retrieval_set_name = SETTINGS['filenames']["retrieval_set_name"]

ref_in_filename = SETTINGS['filenames']["ref_in_fname"]  # used as reference in output filename

projectname = SETTINGS['project']['name']
folderprefix = SETTINGS['project']['folderprefix']

startdate = SETTINGS['period']["fromdate"]
enddate = SETTINGS['period']["todate"]

output_bucket = SETTINGS['s3']['outputbucket']

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
# path_to_files = "C:/Users/developer/OneDrive/@pvln_coding_PVE/myPolygons/"
# path_to_files = "C:/Users/pierre/OneDrive/@pvln_coding_PVE/myPolygons/"

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

# what to do with output files; reread them?
# reread_csv = SETTINGS['output']["output_to_excel"] #False levert mog problemen op


# # check if output folder exists. If not create it.
# if not os.path.exists(output_dir):
#     os.makedirs(output_dir)
#
# # check if temp output folder exists. If not create it.
# if not os.path.exists(output_tmp):
#     os.makedirs(output_tmp)

# DEZE KAN ER UIT...
# fileswanted = baselineAIS.create_fileslist(retrieval_set_name+".json", path_to_files)
# if full_verbose:
#    print(fileswanted)

####################################
#
# STATISTICS OUTPUT
#
####################################

#
#  (re)load the data (always csv), as exel might not contain all data or is not present at all
#
input_filename = output_dir+ref_in_filename + "_" + the_hostname + "_" + projectname + "_AIS_extended"
# statistics_output = pd.read_csv(input_filename+".csv", index_col=0)
# statistics_output = statistics_output.reset_index(drop=True)
statistics_output = pd.read_csv(input_filename+".csv")

if full_verbose:
    print(statistics_output.columns)

statistics_output['date'] = pd.to_datetime(statistics_output['local_time_str'], format='%Y-%m-%d')
statistics_output['date'] = statistics_output['date'].dt.strftime('%Y-%m-%d')
statistics_output['local_time'] = pd.to_datetime(statistics_output['local_time_str'])
if full_verbose:
    print(len(statistics_output))
    print(statistics_output[['name', 'local_time', 'location_zone']])

statistics_output.sort_values(['name', 'local_time'], ascending=[True, True], inplace=True)
if full_verbose:
    print(statistics_output)

statistics_output['delta'] = (statistics_output['local_time']-statistics_output['local_time'].shift()).fillna(pd.Timedelta(seconds=0))
if full_verbose:
    print(statistics_output)

# save the df to s3
wr.s3.to_csv(df=statistics_output,
             index=False,
             path='s3://' + output_bucket + "/" + folderprefix + "/" + ref_in_filename + "/details/" + the_hostname + "_" + projectname + "_statistics_output1.csv"
             )

if os.environ.get("AWS_EXECUTION_ENV") is None:
    # save df also to local disk for further processing

    # check if output folder exists. If not create it.
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_filename = output_dir+ref_in_filename + "_" + the_hostname + "_" + projectname + "_statistics_output1"
    # extended data output files
    statistics_output.to_csv(output_filename+".csv")
    if output_to_excel and len(statistics_output.index) < max_excel_lines:
        statistics_output.to_excel(output_filename+".xlsx")

# https://stackoverflow.com/questions/37504605/timestamps-into-sessions-pandas

gt_tst = statistics_output['local_time'].diff() > pd.Timedelta(hours=session_border)

# diff_user = statistics_output['name'].diff() > 0
# or
diff_user = statistics_output['mmsi'] != statistics_output['mmsi'].shift()

session_id = (diff_user | gt_tst).cumsum()

statistics_output['session_id'] = session_id
statistics_output['session_id_final'] = statistics_output['session_id'].apply(str).apply(lambda x: x.zfill(4)) + "-" + statistics_output['mmsi'].apply(str) + "_" + projectname + "_" + ref_in_filename

if full_verbose:
    print(statistics_output)

# save the df to s3
wr.s3.to_csv(df=statistics_output,
             index=False,
             path='s3://' + output_bucket + "/" + folderprefix + "/" + ref_in_filename + "/details/" + the_hostname + "_" + projectname + "_statistics_output2.csv"
             )

if os.environ.get("AWS_EXECUTION_ENV") is None:
    # save df also to local disk for further processing

    # check if output folder exists. If not create it.
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_filename = output_dir + ref_in_filename + "_" + the_hostname + "_" + projectname + "_statistics_output2"
    # extended data output files
    statistics_output.to_csv(output_filename+".csv")
    if output_to_excel and len(statistics_output.index) < max_excel_lines:
        statistics_output.to_excel(output_filename+".xlsx")

pivot_table = pd.pivot_table(statistics_output,
                             values=['locations_set', 'local_time'],
                             index=['session_id_final', 'mmsi', 'name', 'location_name', 'location_type', 'location_zone'],
                             aggfunc={'locations_set': 'count',
                                      'local_time': [min, max]})


if full_verbose:
    print(pivot_table)

# flatten the pivot table
statistics_output = pd.DataFrame(pivot_table.to_records())
if full_verbose:
    print(statistics_output.head(5))

# change headers
statistics_output.columns = [hdr.replace("('", "").replace("', '", "_").replace("')", "") for hdr in statistics_output.columns]

if full_verbose:
    print(statistics_output.head(5))
    print(statistics_output.columns)

statistics_output['time_diff'] = pd.to_datetime(statistics_output['local_time_max']) - pd.to_datetime(statistics_output['local_time_min'])
statistics_output['time_diff_str'] = statistics_output['time_diff'].apply(str)

if full_verbose:
    print(statistics_output.head(5))

statistics_output = report_output.add_shipinfo(inputdf=statistics_output,
                                               reference_dir=ref_dir,
                                               reference_filename="ship_info.xlsx",
                                               verbose=False)

# ## DEZE GAAT NOG FOUT !!!!!
# #statistics_output=report_output.add_shipinfo_v2(inputdf=statistics_output,
# #                      reference_dir="",
# #                      reference_filename="",
# #                      verbose=False)

df_missing_ships = report_output.missing_info(inputdf=statistics_output,
                                              check_column='registratie-land',
                                              verbose=True)

# ## IS ONDERSTAANDE WEL NODIG ???
# ##add country of registration
# #statistics_output['reg_country']= statistics_output['mmsi'].apply(report_output.countrystring)


# if full_verbose:
#    print('## reg_country column added ##')
#    print(statistics_output.head(5))                                            

# ###################
# THIS IS WHERE ACTUAL OUTPUT STARTS
# ###################

# save the df to s3
wr.s3.to_csv(df=statistics_output,
             index=False,
             path='s3://' + output_bucket + "/" + folderprefix + "/" + ref_in_filename + "/details/" + the_hostname + "_" + projectname + "_statistics_output.csv"
             )

# check if not running as Lambda function
# https://stackoverflow.com/questions/36287374/how-to-check-if-python-app-is-running-within-aws-lambda-function
#
if os.environ.get("AWS_EXECUTION_ENV") is None:
    # save df also to local disk for further processing

    # check if output folder exists. If not create it.
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_filename = output_dir + ref_in_filename + "_" + the_hostname + "_" + projectname + "_statistics_output"
    # extended data output files
    statistics_output.to_csv(output_filename+".csv")
    if output_to_excel and len(statistics_output.index) < max_excel_lines:
        statistics_output.to_excel(output_filename+".xlsx")

# OLD # path = 's3://' + output_bucket + "/" + folderprefix + "/" + ref_in_filename + "/details/" + the_hostname + "_" + projectname + "_missing_ships_info.csv"

filekey = folderprefix + "/" + ref_in_filename + "/details/" + the_hostname + "_" + projectname + "_missing_ships_info"
s3_path = 's3://' + output_bucket + "/" + filekey
if len(df_missing_ships) > 0:
    # save the df to s3
    wr.s3.to_csv(df=df_missing_ships, index=False, path=s3_path + ".csv")
    if output_to_excel and len(df_missing_ships.index) < max_excel_lines:
        wr.s3.to_excel(df=df_missing_ships, index=False, path=s3_path + ".xlsx")
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

### OLD CAN BE REMOVED
# if len(df_missing_ships) > 0:
#     # save the df to s3
#     wr.s3.to_csv(df=df_missing_ships,
#                  index=False,
#                  path='s3://' + output_bucket + "/" + folderprefix + "/" + ref_in_filename + "/details/" + the_hostname + "_" + projectname + "_missing_ships_info.csv"
#                  )

# # check if not running as Lambda function
# # https://stackoverflow.com/questions/36287374/how-to-check-if-python-app-is-running-within-aws-lambda-function
# #
# if os.environ.get("AWS_EXECUTION_ENV") is None:
#     # save df also to local disk for further processing
#
#     # check if output folder exists. If not create it.
#     if not os.path.exists(output_dir):
#         os.makedirs(output_dir)
#
#     output_filename = output_dir + ref_in_filename + "_" + the_hostname + "_" + projectname + "_missing_ships_info"
#     # extended data output files
#     df_missing_ships.to_csv(output_filename+".csv")
#     if output_to_excel and len(df_missing_ships.index) < max_excel_lines:
#         df_missing_ships.to_excel(output_filename+".xlsx", index=False)

# =======================
# To file
# =======================
output_filename = output_dir + ref_in_filename + "/" + the_hostname + "_" + projectname + "_missing_ships_info"
# check if not running as Lambda function
# https://stackoverflow.com/questions/36287374/how-to-check-if-python-app-is-running-within-aws-lambda-function
#
if os.environ.get("AWS_EXECUTION_ENV") is None:
    # save df also to local disk for further processing

    # check if output folder exists. If not create it.
    if not os.path.exists(output_dir + ref_in_filename):
        os.makedirs(output_dir + ref_in_filename)

    if len(df_missing_ships) > 0:
        # extended data output files
        df_missing_ships.to_csv(output_filename+".csv", index=False)
        if output_to_excel and len(df_missing_ships.index) < max_excel_lines:
            df_missing_ships.to_excel(output_filename+".xlsx", index=False)
    else:
        print("Removing files if they exist", output_filename)
        if os.path.exists(output_filename+".csv"):
            os.remove(output_filename+".csv")
        if os.path.exists(output_filename+".xlsx"):
            os.remove(output_filename+".xlsx")
