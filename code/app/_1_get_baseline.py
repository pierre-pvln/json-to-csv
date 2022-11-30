# basic stuff
import os
import json
import socket

import datetime
from typing import cast, List

# data science stuff
import pandas as pd

# aws stuff
import boto3
import awswrangler as wr


def get_filename_datetime():
    now = datetime.datetime.now()
    return str(now.year) + "/" + str(now.month).zfill(2) + "/" + str(now.day).zfill(2) + "/" + "raw-" + now.strftime("%Y-%m-%d_%H:%M:%S")


def create_dateslist(startdate, enddate):
    '''
    Returns a list of dates
    Starting 1 day before the startdate and ending 1 day after the enddate.
    This approach is needed as we convert UTC to local time later on
    '''

    # day before start date
    first_date = datetime.datetime.strptime(startdate, "%Y-%m-%d") - datetime.timedelta(days=1)

    # day after last date
    print(datetime.datetime.strptime(enddate, "%Y-%m-%d"))
    print(datetime.datetime.now())
    if datetime.datetime.strptime(enddate, "%Y-%m-%d") >=  datetime.datetime.now():
        last_date = datetime.datetime.now()
        print("enddate >= now())
        print("enddate   :",enddate)
        print(datetime.datetime.strptime(enddate, "%Y-%m-%d"))
        print("last_date :",last_date)
    else:
        last_date = datetime.datetime.strptime(enddate, "%Y-%m-%d") + datetime.timedelta(days=1)
        print("enddate < now())
        print("enddate   :",enddate)
        print(datetime.datetime.strptime(enddate, "%Y-%m-%d"))
        print("last_date :",last_date)
    
    dates_list = []
    step = datetime.timedelta(days=1)
    while first_date <= last_date:
        print(first_date)
        dates_list.append([first_date.year, first_date.month, first_date.day])
        first_date += step
    return dates_list


def s3_list(bucket_name: str, prefix: str, *, limit: int = cast(int, float("inf"))) -> List[dict]:
    """Return a list of S3 object summaries."""
    # Ref: https://stackoverflow.com/a/57718002/

    print(bucket_name)
    print(prefix)

    contents: List[dict] = []
    continuation_token = None
    if limit <= 0:
        return contents
    while True:
        max_keys = min(1000, limit - len(contents))
        request_kwargs = {"Bucket": bucket_name, "Prefix": prefix, "MaxKeys": max_keys}
        if continuation_token:
            response = _S3_CLIENT.list_objects_v2(**request_kwargs, ContinuationToken=continuation_token)
        else:
            response = _S3_CLIENT.list_objects_v2(**request_kwargs)
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
        contents.extend(response["Contents"])
        is_truncated = response["IsTruncated"]
        if (not is_truncated) or (len(contents) >= limit):
            break
        continuation_token = response["NextContinuationToken"]
    assert len(contents) <= limit
    return contents


# Get the project settings
# ========================

settingsfile = "projectsettings.json"
# Read settings from json file
with open(settingsfile, 'r') as jsonf:
    SETTINGS = json.load(jsonf)

projectname = SETTINGS['project']['name']
folderprefix = SETTINGS['project']['folderprefix']
polygonset = SETTINGS['project']['polygonset']

process_from_date = SETTINGS['period']['fromdate']
process_to_date = SETTINGS['period']['todate']

ref_in_filename = SETTINGS['filenames']['ref_in_fname']

input_bucket = SETTINGS['s3']['inputbucket']
input_region = SETTINGS['s3']['inputregion']

output_bucket = SETTINGS['s3']['outputbucket']
output_region = SETTINGS['s3']['outputregion']

polygon_bucket = SETTINGS['s3']['polygonbucket']
polygon_region = SETTINGS['s3']['polygonregion']

date_type = SETTINGS['s3']['date_type']

lat_min = float(SETTINGS['boundingbox']['lat_min'])
lat_max = float(SETTINGS['boundingbox']['lat_max'])
lon_min = float(SETTINGS['boundingbox']['lon_min'])
lon_max = float(SETTINGS['boundingbox']['lon_max'])

output_dir = SETTINGS['folders']['output_dir']

the_hostname = socket.gethostname()
print('running on   : '+the_hostname)

if the_hostname != 'ip-10-0-1-5':
    # were probably running local so we need credentials
    # get settings for aws profile from environment variables
    profile_name = os.environ.get("AWS_PROFILE_NAME")
    boto3.setup_default_session(profile_name=os.environ.get("AWS_PROFILE_NAME"))
    print("profile_name : "+profile_name)

_S3_CLIENT = boto3.client("s3")

# copy project settingsfile also to s3 for future reference
s3_response = _S3_CLIENT.upload_file(settingsfile, output_bucket, folderprefix + "/" + ref_in_filename + "/" + settingsfile)

# TODO don't use boudingbox settings but get bouding box info from files in set
#    bucket_object = _S3_CLIENT.get_object(Bucket=polygon_bucket, Key='sets/'+polygonset)
#    serializedobject = bucket_object['Body'].read()
#    SETS = json.loads(serializedobject)
#    files_wanted_list = []
#    for entry in SETS:
#        if entry != 'description':
#            for files in SETS[entry]:
#                if len(SETS[entry]['files']) > 0:
#                    for file in SETS[entry]['files']:
#                        files_wanted_list.append([entry+"/"+file])
#    print("polygon files")
#    print(files_wanted_list)

output_df = pd.DataFrame()

# create a list of all the dates for which data should be processed
dates_wanted = create_dateslist(process_from_date, process_to_date)
print(dates_wanted)

for a_day in dates_wanted:
    print("working on day:")
    print(a_day)
    if date_type == "no0":  # trappswise sets
        folder_prefix = str(a_day[0]) + "/" + str(a_day[1]) + "/" + str(a_day[2]) + "/"
    if date_type == "leading0":  # ipheion sets
        folder_prefix = str(a_day[0]) + "/" + str(a_day[1]).zfill(2) + "/" + str(a_day[2]).zfill(2) + "/"
    print(folder_prefix)

    print(input_bucket)
    files_dict = s3_list(input_bucket, folder_prefix, limit=10000)
    for a_file in files_dict:
        print(a_file['Key'])

        bucket_object = _S3_CLIENT.get_object(Bucket=input_bucket,
                                              Key=a_file['Key'])

        serializedobject = bucket_object['Body'].read()
        file_contents = json.loads(serializedobject)

        if file_contents[0]['ERROR'] is not True:  # file should contain some data
            input_df = pd.DataFrame.from_records(file_contents[1])
            # print(input_df)
            if len(input_df) > 1:  # valid data input. Sometimes file with no records.
                filtered_df = input_df[(((input_df['LATITUDE'] > lat_min) & (input_df['LATITUDE'] < lat_max)) & ((input_df['LONGITUDE'] > lon_min) & (input_df['LONGITUDE'] < lon_max)))]
                if len(filtered_df.index) > 0:  # some records found
                    #
                    # TODO add source of data WHY??
                    # filtered_df['datasource'] = a_file['Key']
                    #
                    # print(filtered_df)
                    output_df = output_df.append(filtered_df)
                    output_df.drop_duplicates(inplace=True, ignore_index=True)

# some final cleanup
# add projectname column
output_df['locations_set'] = projectname
# set columnnames to lowercase
output_df.columns = output_df.columns.str.lower()
# rename columns
output_df = output_df.rename(columns={'time': 'ships_time_UTC', 'longitude': 'longitude_val', 'latitude': 'latitude_val'})
# sort on mmsi and date
output_df.sort_values(by=['mmsi', 'ships_time_UTC'], inplace=True, ignore_index=True)

# save the df to s3
wr.s3.to_csv(df=output_df,
             index=False,
             path='s3://' + output_bucket + "/" + folderprefix + "/" + ref_in_filename + "/details/" + the_hostname + "_" + projectname + "_AIS_baseline.csv"
             )

# check if not running as Lambda function
# https://stackoverflow.com/questions/36287374/how-to-check-if-python-app-is-running-within-aws-lambda-function
#
if os.environ.get("AWS_EXECUTION_ENV") is None:
    # save df also to local disk for further processing

    # check if output folder exists. If not create it.
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_filename = output_dir + ref_in_filename + "_" + the_hostname + "_" + projectname + "_AIS_baseline"
    # extended data output files
    output_df.to_csv(output_filename + ".csv")
