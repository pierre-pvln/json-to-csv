import pandas as pd
import geopandas as gpd
import datetime

from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from shapely.ops import unary_union

def add_geozones_to_points(inputdf,files_wanted_list,verbose=False):
    ''' 
    some info text
    '''

    inputdf['in_required_geozone']=0
    inputdf['location_name']=""
    inputdf['location_type']=""
    inputdf['location_zone']=""
    
    #loop trough all files
    for filename in files_wanted_list:
        fname=str(filename).replace("['",'').replace("']",'')
        df_location = gpd.read_file(fname)
        
        locationid  = df_location['Identification'][0]
        locationname = df_location['Name'][0]
        locationtype = df_location['Type'][0]      
        
        if verbose: 
            print(locationid)
            print(locationname)
            print(locationtype)
            
        #create geozone column
        inputdf[locationid]=0
        
        #loop trough all the rows , and set row value to 1 if in that geozone and add teh location name
        for row in inputdf.itertuples():
            testpoint=Point(row.longitude_val,row.latitude_val)
            #print(testpoint)
            if testpoint.within(Polygon(unary_union(df_location['geometry']))):
                inputdf.at[row.Index, locationid] = 1
                
                inputdf.at[row.Index, 'location_name'] = locationname
                inputdf.at[row.Index, 'location_type'] = locationtype
                inputdf.at[row.Index, 'location_zone'] = locationid
                
                
        inputdf['in_required_geozone'] = inputdf['in_required_geozone'] + inputdf[locationid]
        # for any point not in geozone, inputdf['in_required_geozone']=0
        
    return inputdf


def remove_points_not_in_geozone(inputdf,verbose=False):

    # inspiration: https://thispointer.com/python-pandas-how-to-drop-rows-in-dataframe-by-conditions-on-column-values/
    
    indexList = inputdf[ inputdf['in_required_geozone'] == 0 ].index

    if verbose : print('Length original df: '+str(len(inputdf)))
        
    # Delete these row indexes from dataFrame
    inputdf.drop(indexList , inplace=True)

    if verbose : print('Length new      df: '+str(len(inputdf)))
    
    return inputdf

def select_dates(inputdf,start,end,verbose=False):
    '''
    select only rows in date period
    '''

    startdt=pd.Timestamp(start).tz_localize('Europe/Amsterdam')
    
    # add a day otherwise that last end date is not included. (Defaults to 00:00:00)
    enddt=pd.Timestamp(end).tz_localize('Europe/Amsterdam') + datetime.timedelta(days=1)
    
    if verbose : 
        print(startdt)
        print(enddt)
        print(inputdf['local_time'])
    
    #select dates out of dates range
    indexList = inputdf[ (inputdf['local_time'] <= startdt) | (inputdf['local_time'] >= enddt) ].index

    if verbose : print('Lenght original df    : '+str(len(inputdf)))
        
    # Delete these row indexes from dataFrame
    inputdf.drop(indexList , inplace=True)

    if verbose : print('Lenght after selection: '+str(len(inputdf)))
    
    return inputdf  

def add_shiptype(inputdf,reference_dir,reference_filename,verbose=False):
    '''
    Add AIS ships type description to dataset
    '''
    
    df_ais_ship_types = pd.read_excel(reference_dir+reference_filename)
    
    extdf = pd.merge(left=inputdf, right=df_ais_ship_types, how='left', left_on='type', right_on='AIS_SHIPTYPE')
    extdf.drop(['AIS_SHIPTYPE', 'AIS_TYPE_NAME', 'AIS_DETAILED_TYPE'], axis=1, inplace=True)

    # replace NaN's
    extdf.fillna("Unknown",inplace=True)

    if verbose :
        print(extdf.head(5))
        print(extdf.tail(5))

    return extdf

def add_shiptype_v2(inputdf,reference_dir="",reference_filename="",AIStype="summary",verbose=False):
    '''
    Add AIS ships type description to dataset
    Inspiration: https://stackoverflow.com/questions/20250771/remap-values-in-pandas-column-with-a-dict
	
	type: "name" (first value) or "summary" (second value)  
	
    '''
    AIS_shiptype_dict={
        '10':['Reserved','Unspecified'],
        '11':['Reserved','Unspecified'],
        '12':['Reserved','Unspecified'],
        '13':['Reserved','Unspecified'],
        '14':['Reserved','Unspecified'],
        '15':['Reserved','Unspecified'],
        '16':['Reserved','Unspecified'],
        '17':['Reserved','Unspecified'],
        '18':['Reserved','Unspecified'],
        '19':['Reserved','Unspecified'],
        '20':['Wing In Grnd','Wing in Grnd'],
        '21':['Wing In Grnd','Wing in Grnd'],
        '22':['Wing In Grnd','Wing in Grnd'],
        '23':['Wing In Grnd','Wing in Grnd'],
        '24':['Wing In Grnd','Wing in Grnd'],
        '25':['Wing In Grnd','Wing in Grnd'],
        '26':['Wing In Grnd','Wing in Grnd'],
        '27':['Wing In Grnd','Wing in Grnd'],
        '28':['Wing In Grnd','Wing in Grnd'],
        '29':['SAR Aircraft','Search and Rescue'],
        '30':['Fishing','Fishing'],
        '31':['Tug','Tug'],
        '32':['Tug','Tug'],
        '33':['Dredger','Special Craft'],
        '34':['Dive Vessel','Special Craft'],
        '35':['Military Ops','Special Craft'],
        '36':['Sailing Vessel','Sailing Vessel'],
        '37':['Pleasure Craft','Pleasure Craft'],
        '38':['Reserved','Unspecified'],
        '39':['Reserved','Unspecified'],
        '40':['High-Speed Craft','High-Speed Craft'],
        '41':['High-Speed Craft','High-Speed Craft'],
        '42':['High-Speed Craft','High-Speed Craft'],
        '43':['High-Speed Craft','High-Speed Craft'],
        '44':['High-Speed Craft','High-Speed Craft'],
        '45':['High-Speed Craft','High-Speed Craft'],
        '46':['High-Speed Craft','High-Speed Craft'],
        '47':['High-Speed Craft','High-Speed Craft'],
        '48':['High-Speed Craft','High-Speed Craft'],
        '49':['High-Speed Craft','High-Speed Craft'],
        '50':['Pilot Vessel','Special Craft'],
        '51':['SAR','Search and Rescue'],
        '52':['Tug','Tug'],
        '53':['Port Tender','Special Craft'],
        '54':['Anti-Pollution','Special Craft'],
        '55':['Law Enforce','Special Craft'],
        '56':['Local Vessel','Special Craft'],
        '57':['Local Vessel','Special Craft'],
        '58':['Medical Trans','Special Craft'],
        '59':['Special Craft','Special Craft'],
        '60':['Passenger','Passenger'],
        '61':['Passenger','Passenger'],
        '62':['Passenger','Passenger'],
        '63':['Passenger','Passenger'],
        '64':['Passenger','Passenger'],
        '65':['Passenger','Passenger'],
        '66':['Passenger','Passenger'],
        '67':['Passenger','Passenger'],
        '68':['Passenger','Passenger'],
        '69':['Passenger','Passenger'],
        '70':['Cargo','Cargo'],
        '71':['Cargo - Hazard A (Major)','Cargo'],
        '72':['Cargo - Hazard B','Cargo'],
        '73':['Cargo - Hazard C (Minor)','Cargo'],
        '74':['Cargo - Hazard D (Recognizable)','Cargo'],
        '75':['Cargo','Cargo'],
        '76':['Cargo','Cargo'],
        '77':['Cargo','Cargo'],
        '78':['Cargo','Cargo'],
        '79':['Cargo','Cargo'],
        '80':['Tanker','Tanker'],
        '81':['Tanker - Hazard A (Major)','Tanker'],
        '82':['Tanker - Hazard B','Tanker'],
        '83':['Tanker - Hazard C (Minor)','Tanker'],
        '84':['Tanker - Hazard D (Recognizable)','Tanker'],
        '85':['Tanker','Tanker'],
        '86':['Tanker','Tanker'],
        '87':['Tanker','Tanker'],
        '88':['Tanker','Tanker'],
        '89':['Tanker','Tanker'],
        '90':['Other','Other'],
        '91':['Other','Other'],
        '92':['Other','Other'],
        '93':['Other','Other'],
        '94':['Other','Other'],
        '95':['Other','Other'],
        '96':['Other','Other'],
        '97':['Other','Other'],
        '98':['Other','Other'],
        '99':['Other','Other']
    }
    
    # use the default settings if filename is not given
    if reference_filename == "":
        if verbose: print("Using default AIS shiptype mapping function.")
        
        whichlist = 1
        if AIStype == "name": whichlist = 0
        
        # create new column where info is to be placed
        # do that by copying existing column
        # than mapping function on new column
        
        # create the dict with the required info` 
        Inner_dict = dict(map(lambda x: (x[0], x[1][whichlist]), AIS_shiptype_dict.items() ))
        
        inputdf['AIS_TYPE_SUMMARY']=inputdf['type'].map(Inner_dict)
        extdf=inputdf.copy()
        
    else:
        if verbose:
            print("Using default file as input.")
        df_ais_ship_types = pd.read_excel(reference_dir+reference_filename,
                                          engine='openpyxl'
                                          )

        extdf = pd.merge(left=inputdf, right=df_ais_ship_types, how='left', left_on='type', right_on='AIS_SHIPTYPE')
        extdf.drop(['AIS_SHIPTYPE', 'AIS_TYPE_NAME', 'AIS_DETAILED_TYPE'], axis=1, inplace=True)

        # replace NaN's
        extdf.fillna("Unknown",inplace=True)

    if verbose:
        print(extdf.head(5))
        print(extdf.tail(5))

    return extdf

def add_navstat(inputdf,reference_dir,reference_filename,verbose=False):
    '''
    Add AIS navstat to dataset
    '''
    
    df_ais_navstat = pd.read_excel(reference_dir+reference_filename)
    
    extdf = pd.merge(left=inputdf, right=df_ais_navstat, how='left', left_on='navstat', right_on='AIS_NAVSTAT_VALUE')
    extdf.drop(['AIS_NAVSTAT_VALUE'], axis=1, inplace=True)

    # replace NaN's
    extdf.fillna("Unknown",inplace=True)
    
    if verbose :
        print(extdf.head(5))
        print(extdf.tail(5))
    
    return extdf

def add_navstat_v2(inputdf,reference_dir="",reference_filename="",verbose=False):
    '''
    Add AIS navstat to dataset
    Inspiration: https://stackoverflow.com/questions/20250771/remap-values-in-pandas-column-with-a-dict
    '''
    AIS_navstat_dict={ 
    0  : 'Under way using engine',
    1  : 'At anchor',
    2  : 'Not under command',
    3  : 'Restricted manoeuverability',
    4  : 'Constrained by her draught',
    5  : 'Moored',
    6  : 'Aground',
    7  : 'Engaged in Fishing',
    8  : 'Under way sailing',
    9  : 'Reserved for future amendment of Navigational Status for HSC',
    10 : 'Reserved for future amendment of Navigational Status for WIG',
    11 : 'Reserved for future use',
    12 : 'Reserved for future use',
    13 : 'Reserved for future use',
    14 : 'AIS-SART is active',
    15 : 'Not defined (default)',
    }
    
    # use the default settings if filename is not given
    if reference_filename == "":
        if verbose: print("Using default AIS navstat mapping function.")
        # create new column where info is to be placed
        # do that by copying existing column
        # than mapping function on new column
        inputdf['AIS_NAVSTAT_DESCRIPTION']=inputdf['navstat'].map(AIS_navstat_dict)
        extdf=inputdf.copy()

    else:
        if verbose: print("Using default file as input.")    
        df_ais_navstat = pd.read_excel(reference_dir+reference_filename)

        extdf = pd.merge(left=inputdf, right=df_ais_navstat, how='left', left_on='navstat', right_on='AIS_NAVSTAT_VALUE')
        extdf.drop(['AIS_NAVSTAT_VALUE'], axis=1, inplace=True)

        # replace NaN's
        extdf.fillna("Unknown",inplace=True)
    
    if verbose :
        print(extdf.head(5))
        print(extdf.tail(5))
    
    return extdf