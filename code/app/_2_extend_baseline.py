# basic stuff
import os
import json
import socket
import getpass

# data science stuff
import pandas as pd

# aws stuff
import boto3
import awswrangler as wr

# import the modules to wrangle the data
import my_utils
import extendAIS

# Get the project settings
# ========================

settingsfile = "projectsettings.json"
# Read settings from json file
with open(settingsfile, 'r') as jsonf:
    SETTINGS = json.load(jsonf)

ref_in_filename = SETTINGS['filenames']["ref_in_fname"]  # used as reference in output filename

projectname = SETTINGS['project']['name']
folderprefix = SETTINGS['project']['folderprefix']

startdate = SETTINGS['period']["fromdate"]
enddate = SETTINGS['period']["todate"]

output_bucket = SETTINGS['s3']['outputbucket']

# Save statistics data, needed for SFTP
yearfolder = SETTINGS['output']["yearfolder"]
municipality = SETTINGS['output']["municipality"]

# # timedelta to check if same session
# # the maximum time between 2 registrations to be seen as one session
# session_border = SETTINGS['calculations']["session_border_in_hours"]

# folders for output
ref_dir = SETTINGS['folders']["ref_dir"]
output_dir = SETTINGS['folders']["output_dir"]
# output_tmp = SETTINGS['folders']["output_tmp"]

# folder for settings
settings_dir = SETTINGS['folders']["settings_dir"]

username = getpass.getuser()
if username == 'developer':
    path_to_files = "C:/Users/developer/OneDrive/@pvln_coding_PVE/myPolygons/"
if username == 'ubuntu':
    path_to_files = "/home/ubuntu/polygons/"

# # path_to_files="/home/developer/myPolygons/"
# # path_to_files="C:/Users/pierr_8jj0nf8/OneDrive/@pvln_coding_PVE/myPolygons/"
# path_to_files = "C:/Users/developer/OneDrive/@pvln_coding_PVE/myPolygons/"
# # path_to_files = "C:/Users/pierre/OneDrive/@pvln_coding_PVE/myPolygons/"
# path_to_files="/home/ubuntu/polygons/"

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

# TODO Remove is done at the end
# # check if output folder exists. If not create it.
# if not os.path.exists(output_dir):
#     os.makedirs(output_dir)

# TODO Remove from code and project settings
# check if temp output folder exists. If not create it.
# if not os.path.exists(output_tmp):
#     os.makedirs(output_tmp)

fileswanted = my_utils.create_fileslist(projectname + ".json", path_to_files)
if full_verbose:
    print(fileswanted)

# ###################################
#
# EXTEND AIS BASELINE
#
# ###################################
#
#  (re)load the data (always csv), as exel might not contain all data or is not present at all
#
input_filename = output_dir + ref_in_filename + "_" + the_hostname + "_" + projectname + "_AIS_baseline"
# ais_extended = pd.read_csv(input_filename+".csv", index_col=0)
# ais_extended = ais_extended.reset_index(drop=True)

# ###
# ###

print(os.getcwd())

ais_extended = pd.read_csv(input_filename+".csv")

if full_verbose:
    print("0 #########################")
    print(ais_extended.columns)

ais_extended = extendAIS.add_geozones_to_points(ais_extended, fileswanted, verbose=True)
ais_extended = extendAIS.remove_points_not_in_geozone(ais_extended, verbose=True)
ais_extended.drop(columns=['in_required_geozone'])


if full_verbose:
    print(ais_extended.columns)

# convert timestring to datetime
# remove ' GMT form time"
ais_extended['ships_time_UTC'] = ais_extended['ships_time_UTC'].str.replace(' GMT', '')

ais_extended['ships_time_UTC'] = pd.to_datetime(ais_extended['ships_time_UTC'],
                                                format='%Y%m%d %H:%M:%S')
# ais_extended['ships_time_UTC'] = pd.to_datetime(ais_extended['ships_time_UTC'],
#                                                format='%Y-%m-%d %H:%M:%S %Z'
#                                                )

# Add local time column based on shipstime which is UTC
ais_extended['local_time'] = ais_extended['ships_time_UTC'].dt.tz_localize('UTC').dt.tz_convert('Europe/Amsterdam')
# ais_extended['local_time'] = ais_extended['ships_time_UTC'].dt.tz_convert('Europe/Amsterdam')
ais_extended['local_time_str'] = ais_extended['local_time'].dt.strftime('%Y-%m-%d %H:%M:%S')

if full_verbose:
    print("1########################")
    print(ais_extended.columns)

ais_extended = extendAIS.select_dates(inputdf=ais_extended,
                                      start=startdate,
                                      end=enddate,
                                      verbose=False)
# ##TESTING
if full_verbose:
    print("2########################")
    print(ais_extended.columns)
ais_extended = extendAIS.add_shiptype_v2(inputdf=ais_extended,
                                         reference_dir=ref_dir,
                                         AIStype="summary",
                                         reference_filename="AIS_shiptype.xlsx",
                                         verbose=False)

# ais_extended=extendAIS.add_navstat_v2(inputdf=ais_extended,
#                      reference_dir=ref_dir,
#                      reference_filename="AIS_navstat.xlsx",
#                      verbose=False)

if full_verbose:
    print("3#########################")
    print(ais_extended.columns)

ais_extended = extendAIS.add_navstat_v2(inputdf=ais_extended,
                                        reference_dir="",
                                        reference_filename="",
                                        verbose=False)

if full_verbose:
    print("4########################")
    print(ais_extended.columns)

ais_extended.drop(['local_time'], axis=1, inplace=True)

if full_verbose:
    print("5########################")
    print(ais_extended.columns)

# save the df to s3
wr.s3.to_csv(df=ais_extended,
             index=False,
             path='s3://' + output_bucket + "/" + folderprefix + "/" + ref_in_filename + "/details/" + the_hostname + "_" + projectname + "_AIS_extended.csv"
             )

# check if not running as Lambda function
# https://stackoverflow.com/questions/36287374/how-to-check-if-python-app-is-running-within-aws-lambda-function
#
if os.environ.get("AWS_EXECUTION_ENV") is None:
    # save df also to local disk for further processing

    # check if output folder exists. If not create it.
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_filename = output_dir + ref_in_filename + "_" + the_hostname + "_" + projectname + "_AIS_extended"
    # extended data output files
    ais_extended.to_csv(output_filename+".csv")
    if output_to_excel and len(ais_extended.index) < max_excel_lines:
        ais_extended.to_excel(output_filename+".xlsx")
