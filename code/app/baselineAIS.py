#basic stuff
import json

#date-time stuff
import datetime

#data and geo stuff
import pandas as pd
import geopandas as gpd

from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from shapely.ops import unary_union

# data access
import mysql.connector

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
    
    
def create_boundingbox(files_wanted_list):
    ''' 
    some info text
    '''
    lat_lon_init = False

    #loop trough all files in folder 
    for filename in files_wanted_list:
        fname=str(filename).replace("['",'').replace("']",'')
       
        df_location = gpd.read_file(fname)

        #https://gis.stackexchange.com/questions/266730/filter-by-bounding-box-in-geopandas
        a_polygon = Polygon(unary_union(df_location['geometry']))  

        bbox = a_polygon.bounds

        #initialize 
        if lat_lon_init != True:
            min_lon = bbox[0]
            min_lat = bbox[1]
            max_lon = bbox[2]
            max_lat = bbox[3]
            lat_lon_init = True


        #(lat,lon)
        # checks are only valid for NL. To make it work for rest of world, additional tests are needed.
        if min_lon > bbox[0]: min_lon = bbox[0]
        if min_lat > bbox[1]: min_lat = bbox[1]
        if max_lon < bbox[2]: max_lon = bbox[2]
        if max_lat < bbox[3]: max_lat = bbox[3]


    latlonmminmax_list = [min_lat,min_lon,max_lat,max_lon]
    
    #Create the bounding box to be able to check it
    lb = Point(min_lon,min_lat)
    rb = Point(max_lon,min_lat)
    lo = Point(min_lon,max_lat)
    ro = Point(max_lon,max_lat)
    pointList = [lb, lo, ro, rb]
    poly = Polygon([[p.x, p.y] for p in pointList])

    # convert polygon to geojson format
    boundingbox_geojson = gpd.GeoSeries([poly]).to_json()

    #display(boundingbox_geojson)

    return boundingbox_geojson, latlonmminmax_list


def retrieve_ships_from_repository(credentialsfile,
                              which_db, which_day, 
                              lat_min, lat_max, lon_min, lon_max,
                              which_locations, 
#                             locationid,
                              tempfile="", verbose=False):
    '''    
    credentialsfile: json file with database access credentials
    which_db       : the database to use (a year_month string)
    which_day      : the day in that month (a table in the database)
    lat_min        : minimum value of latitude
    lat_max        : maximum value of latitude
    lon_min        : minimum value of longitude
    lot_max        : maximum value of longitude
    which_locations: string name
###    locationid     : a name for the location 
    tempfile       : folder + filename where to store temp retrives
    verbose        : show some additional info 
    '''

    ships_from_db_df=pd.DataFrame()
    
    if verbose: display(credentialsfile)    
        
    # Read settings from json file 
    with open(credentialsfile, 'r') as jsonf: 
        SETTINGS = json.load(jsonf)
       
    #settings for db access
    db_host=SETTINGS['database']['host']
    db_user=SETTINGS['database']['user']
    db_pass=SETTINGS['database']['password']    

    cnxn = mysql.connector.connect(user=db_user, password=db_pass, host=db_host, db=which_db)
#   cnxn = mysql.connector.connect(user=db_user, password=db_pass, host=db_host, db=which_db, buffered=True )

    cursor = cnxn.cursor()
    querypart = ("SELECT mmsi, name, callsign, type " + 
                 ", longitude AS longitude_val" +
                 ", latitude AS latitude_val" +
                 ", cog, sog, heading, navstat, draught" + 
                 ", time AS ships_time_UTC" +
                 ", '" + which_locations + "' AS locations_set" +
###                 ", '" + locationid + "' AS location" +
                 " FROM " + "`" + str(which_day).zfill(2) + "`" +
                 " WHERE (longitude >= " + str(lon_min) + " AND longitude <= " + str(lon_max) + ")" +  
                 " AND (latitude >= " + str(lat_min) + " AND latitude <= " + str(lat_max) + ")" +
                 ";")
    if verbose: display(querypart)

    df_from_db = pd.read_sql_query(querypart, cnxn)
    if verbose: display(tempfile)
    if tempfile !="": df_from_db.to_excel(tempfile)
    if verbose: display(df_from_db)

    ships_from_db_df = ships_from_db_df.append(df_from_db, ignore_index=True)
    if verbose: display(len(ships_from_db_df))

    # close database connection
    cnxn.close()

    return(ships_from_db_df)


def create_ais_baseline_df(dates_wanted,
                           db_credentials,
                           min_lat,                           
                           max_lat,
                           min_lon,
                           max_lon,
                           retrieval_set,
                           output_temp,
                           verbose=False):
    ''' 
    some info text
    '''
    
    df_ais_baseline = pd.DataFrame()
    counter = 0
    aantal = 0

    #loop trough all the dates in the list
    for element in dates_wanted:
        if verbose: display(element[0],element[1],element[2])
        year=element[0]
        month=element[1]
        day=element[2]

        aantal = len(df_ais_baseline)

        ### 
        #Get the data
        ###
        the_database=str(year)+ "_" + str(month).zfill(2)
        if verbose: display('database :'+the_database)

        df_ais_baseline = df_ais_baseline.append( retrieve_ships_from_repository( 
                           credentialsfile=db_credentials,
                           which_db=the_database,
                           which_day=day,
                           lat_min=min_lat,                           
                           lat_max=max_lat,
                           lon_min=min_lon,
                           lon_max=max_lon,
                           which_locations=retrieval_set,
                           tempfile=output_temp + datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")+ "_" + retrieval_set + "_" + str(counter).zfill(3)+".xlsx",
                           verbose=verbose), ignore_index=True)


        if verbose: display("run: "+str(day).zfill(2)+"; length added: "+str(len(df_ais_baseline)-aantal))

        counter = counter + 1

    df_ais_baseline.drop_duplicates(inplace=True)

    return df_ais_baseline
