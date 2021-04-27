#basic stuff
import json

#date-time stuff
import datetime

#data and geo stuff
#import pandas as pd

def create_dateslist(startdate,enddate):
    '''
    Returns a list of dates
    Starting 1 day before the startdate and ending 1 day after the enddate.
    This approach is needed as we convert UTC to local time later on
    '''

    #day before start date
    first_date=datetime.datetime.strptime(startdate, "%Y-%m-%d") - datetime.timedelta(days=1)

    #day after last date
    last_date=datetime.datetime.strptime(enddate, "%Y-%m-%d") + datetime.timedelta(days=1)

    dates_list=[]
    step = datetime.timedelta(days=1)
    while first_date <= last_date:
        dates_list.append([first_date.year, first_date.month, first_date.day])
        first_date += step
    return dates_list


def create_fileslist(retrieval_set,
                     path_to_geojson_files):
    ''' 
    some info text
    '''
    # Read sets from json
    with open(path_to_geojson_files+ "/sets/" +retrieval_set, 'r') as jsonf: 
        SETS = json.load(jsonf)

    files_list=[]
    for entry in SETS:
        if entry != 'description':
            for files in SETS[entry]:
                if len(SETS[entry]['files']) > 0:
                    for file in SETS[entry]['files']:
                        files_list.append([path_to_geojson_files+entry+"/"+file])
    return files_list  
    