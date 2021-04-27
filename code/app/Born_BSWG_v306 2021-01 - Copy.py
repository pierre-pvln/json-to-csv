#!/usr/bin/env python
# coding: utf-8

# # BORN BSWG BESTAND GENEREREN

# In[1]:


# REQUIRED PARAMETERS
#####################

retrieval_set_name="NL-Born-BSGW"
ref_in_fname="2021-01" # used as reference in output filename

startdate="2021-01-01"
enddate="2021-01-31"
#enddate="2020-9-1"


# Save statistics data, needed for SFTP
yearfolder=2021
municipality="Born"

#timedelta to check if same session 
# the maximum time between 2 registrations to be seen as one session
session_border=12 #hours


# In[2]:


# OTHER PARAMETERS
###################

# folders for output
ref_dir="../input/"

# folders for output
output_dir="../output/"
output_tmp="../output/temp/"

# folder for settings
settings_dir="../set/"

#path_to_files="/home/developer/myPolygons/"
#path_to_files="C:/Users/pierr_8jj0nf8/OneDrive/@pvln_coding_PVE/myPolygons/"
#path_to_files="C:/Users/developer/OneDrive/@pvln_coding_PVE/myPolygons/"
path_to_files="C:/Users/pierre/OneDrive/@pvln_coding_PVE/myPolygons/"

output_to_excel=True

#https://support.microsoft.com/en-us/office/excel-specifications-and-limits-1672b34d-7043-467e-8e27-269d656771c3
max_excel_lines=1048576 

#debugging
full_verbose=True

#what to do with output files; reread them?
reread_csv=True #False levert mog problemen op


# In[3]:


#basic stuff
import os


# In[4]:


#data science stuff
import pandas as pd


# In[5]:


# check if output folder exists. If not create it.
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# check if temp output folder exists. If not create it.
if not os.path.exists(output_tmp):
    os.makedirs(output_tmp)


# In[6]:


#import the modules to wrangle the data
import baselineAIS
import extendAIS
import report_output
import financial_output


# In[7]:


####################################
#
# GET AIS BASELINE
#
####################################


# In[8]:


dateswanted=baselineAIS.create_dateslist(startdate,enddate)
if full_verbose: display(dateswanted)


# In[9]:


fileswanted=baselineAIS.create_fileslist(retrieval_set_name+".json",path_to_files)
if full_verbose: display(fileswanted)


# In[10]:


boundingbox_info=baselineAIS.create_boundingbox(fileswanted)
if full_verbose: display(boundingbox_info)


# In[11]:


# save boundingbox info as geojson file
output_filename = output_dir+ref_in_fname+"_BB_"+retrieval_set_name+'.geojson'
with open(output_filename, 'w') as output_file:
    output_file.write(format(boundingbox_info[0]))


# In[12]:


ais_baseline=baselineAIS.create_ais_baseline_df(dateswanted,
                                                 db_credentials=settings_dir+'settings.json',
                                                 min_lat=boundingbox_info[1][0],
                                                 min_lon=boundingbox_info[1][1],
                                                 max_lat=boundingbox_info[1][2],
                                                 max_lon=boundingbox_info[1][3],
                                                 retrieval_set=retrieval_set_name,
                                                 #location_id="in boundingbox",
                                                 output_temp=output_tmp,
                                                 verbose=True)


# In[13]:


if full_verbose: display(ais_baseline.columns)


# In[14]:


output_filename = output_dir+ref_in_fname+"_"+retrieval_set_name+"_AIS_baseline"
#basic data output files
ais_baseline.to_csv(output_filename+".csv")
if output_to_excel and len(ais_baseline.index) < max_excel_lines: 
    ais_baseline.to_excel(output_filename+".xlsx")


# In[15]:


####################################
#
# EXTEND AIS BASELINE
#
####################################


# In[16]:


#
#  (re)load the data (always csv), as exel might not contain all data or is not present at all
#
if reread_csv:
    input_filename=output_dir+ref_in_fname+"_"+retrieval_set_name+"_AIS_baseline"
    ais_extended=pd.read_csv(input_filename+".csv",index_col=0)
    ais_extended=ais_extended.reset_index(drop=True)
else:
    ais_extended=ais_baseline.copy()


# In[17]:


ais_extended = extendAIS.add_geozones_to_points(ais_extended,fileswanted,verbose=True) 
ais_extended = extendAIS.remove_points_not_in_geozone(ais_extended,verbose=True)
ais_extended.drop(columns=['in_required_geozone'])

if full_verbose: display(ais_extended.columns)


# In[18]:


# convert timestring to datetime
ais_extended['ships_time_UTC'] = pd.to_datetime(ais_extended['ships_time_UTC'], format='%Y%m%d %H:%M:%S')
# Add local time column based on shipstime which is UTC
ais_extended['local_time']=ais_extended['ships_time_UTC'].dt.tz_localize('UTC').dt.tz_convert('Europe/Amsterdam')
ais_extended['local_time_str']=ais_extended['local_time'].dt.strftime('%Y-%m-%d %H:%M:%S')


# In[19]:


ais_extended=extendAIS.select_dates(inputdf=ais_extended,
                                 start= startdate,
                                 end= enddate,
                                 verbose=False)


# In[20]:


###TESTING

ais_extended=extendAIS.add_shiptype_v2(inputdf=ais_extended,
                      reference_dir=ref_dir,
                      AIStype="summary", 
                      reference_filename="AIS_shiptype.xlsx",
                      verbose=False)


# In[21]:


#ais_extended=extendAIS.add_navstat_v2(inputdf=ais_extended,
#                      reference_dir=ref_dir,
#                      reference_filename="AIS_navstat.xlsx",
#                      verbose=False)

ais_extended=extendAIS.add_navstat_v2(inputdf=ais_extended,
                      reference_dir="",
                      reference_filename="",
                      verbose=False)


# In[22]:


if full_verbose: display(ais_extended.columns)
ais_extended.drop(['local_time'], axis=1, inplace=True)


# In[23]:


output_filename = output_dir+ref_in_fname+"_"+retrieval_set_name+"_AIS_extended"
#extended data output files
ais_extended.to_csv(output_filename+".csv")
if output_to_excel and len(ais_extended.index) < max_excel_lines: 
    ais_extended.to_excel(output_filename+".xlsx")


# In[24]:


####################################
#
# STATISTICS OUTPUT
#
####################################


# In[25]:


#
#  (re)load the data (always csv), as exel might not contain all data or is not present at all
#
if reread_csv:
    input_filename=output_dir+ref_in_fname+"_"+retrieval_set_name+"_AIS_extended"
    statistics_output=pd.read_csv(input_filename+".csv",index_col=0)
    statistics_output=statistics_output.reset_index(drop=True)
    if full_verbose: display(statistics_output.columns)
else: 
    statistics_output=ais_extended.copy


# In[26]:


statistics_output['date']=pd.to_datetime(statistics_output['local_time_str'],format=('%Y-%m-%d'))
statistics_output['date']=statistics_output['date'].dt.strftime('%Y-%m-%d')
statistics_output['local_time']=pd.to_datetime(statistics_output['local_time_str'])
if full_verbose: display(len(statistics_output))
if full_verbose: display(statistics_output[['name', 'local_time','location_zone']])


# In[27]:


statistics_output.sort_values(['name', 'local_time'], ascending=[True, True], inplace=True)
if full_verbose: display(statistics_output)


# In[28]:


statistics_output['delta'] = (statistics_output['local_time']-statistics_output['local_time'].shift()).fillna(pd.Timedelta(seconds=0))
if full_verbose: display(statistics_output)


# In[29]:


output_filename = output_dir+ref_in_fname+"_"+retrieval_set_name+"_statistics_output1"
#extended data output files
statistics_output.to_csv(output_filename+".csv")
if output_to_excel and len(statistics_output.index) < max_excel_lines: 
    statistics_output.to_excel(output_filename+".xlsx")


# In[30]:


#https://stackoverflow.com/questions/37504605/timestamps-into-sessions-pandas

gt_tst = statistics_output['local_time'].diff() > pd.Timedelta(hours=session_border)

#diff_user = statistics_output['name'].diff() > 0
# or
diff_user = statistics_output['mmsi'] != statistics_output['mmsi'].shift()

session_id = (diff_user | gt_tst).cumsum()

statistics_output['session_id'] = session_id
statistics_output['session_id_final'] = statistics_output['session_id'].apply(str).apply(lambda x: x.zfill(4)) + "-" + statistics_output['mmsi'].apply(str) + "_" + retrieval_set_name + "_" + ref_in_fname


# In[31]:


if full_verbose: display(statistics_output)


# In[32]:


output_filename = output_dir+ref_in_fname+"_"+retrieval_set_name+"_statistics_output2"
#extended data output files
statistics_output.to_csv(output_filename+".csv")
if output_to_excel and len(statistics_output.index) < max_excel_lines: 
    statistics_output.to_excel(output_filename+".xlsx")


# In[33]:


pivot_table = pd.pivot_table(statistics_output, values=['locations_set','local_time' ],
                       index=['session_id_final','mmsi','name','location_name','location_type','location_zone'],
                       aggfunc={'locations_set': 'count',
                                 'local_time': [min, max]})


if full_verbose: display(pivot_table) 


# In[34]:


#flatten the pivot table
statistics_output = pd.DataFrame(pivot_table.to_records())
if full_verbose: display(statistics_output.head(5))

#change headers
statistics_output.columns = [hdr.replace("('","").replace("', '" , "_").replace("')", "")                      for hdr in statistics_output.columns]

if full_verbose: display(statistics_output.head(5)) 
if full_verbose: display(statistics_output.columns)

statistics_output['time_diff']=pd.to_datetime(statistics_output['local_time_max']) - pd.to_datetime(statistics_output['local_time_min'])
statistics_output['time_diff_str']=statistics_output['time_diff'].apply(str)

if full_verbose: display(statistics_output.head(5))
                         


# In[35]:


statistics_output=report_output.add_shipinfo(inputdf=statistics_output,
                      reference_dir=ref_dir,
                      reference_filename="ship_info.xlsx",
                      verbose=False)    


### DEZE GAAT NOG FOUT !!!!!
##statistics_output=report_output.add_shipinfo_v2(inputdf=statistics_output,
##                      reference_dir="",
##                      reference_filename="",
##                      verbose=False)    

df_missing_ships = report_output.missing_info(inputdf=statistics_output,
                                 check_column='registratie-land',
                                 verbose=True)

### IS ONDERSTAANDE WEL NODIG ???
###add country of registration 
##statistics_output['reg_country']= statistics_output['mmsi'].apply(report_output.countrystring)


#if full_verbose: 
#    display('## reg_country column added ##')
#    display(statistics_output.head(5))                                            
    


# In[36]:


output_filename = output_dir+ref_in_fname+"_"+retrieval_set_name+"_statistics_output"
#extended data output files
statistics_output.to_csv(output_filename+".csv")
if output_to_excel and len(statistics_output.index) < max_excel_lines: 
    statistics_output.to_excel(output_filename+".xlsx")


# In[37]:


output_filename = output_dir+ref_in_fname+"_"+retrieval_set_name+"_missing_ships_info"
#extended data output files
df_missing_ships.to_csv(output_filename+".csv")
if output_to_excel and len(df_missing_ships.index) < max_excel_lines: 
    df_missing_ships.to_excel(output_filename+".xlsx",index=False)  


# In[38]:


####################################
#
# BSGW OUTPUT
#
####################################


# In[39]:


#
#  (re)load the data (always csv), as exel might not contain all data or is not present at all
#
if reread_csv:
    input_filename=output_dir+ref_in_fname+"_"+retrieval_set_name+"_statistics_output"
    BSGW_output=pd.read_csv(input_filename+".csv",index_col=0,dtype=str)
    BSGW_output=statistics_output.reset_index(drop=True)
    if full_verbose: display(BSGW_output.dtypes)
else: 
    BSGW_output=statistics_output.copy()


# In[40]:


# keep only quay rows 
indexList = BSGW_output[ (BSGW_output['location_type'] != 'quay') ].index

# Delete these row indexes from dataFrame
BSGW_output.drop(indexList , inplace=True)


# In[41]:


if full_verbose: display(BSGW_output.shape)
if full_verbose: display(BSGW_output)


# In[42]:


if full_verbose: display(BSGW_output.shape)


# In[43]:


BSGW_output=financial_output.add_billing_info(inputdf=BSGW_output,
                          reference_dir=ref_dir,
                          reference_filename="billing_info.xlsx",
                          verbose=True)


# In[44]:


df_missing_billing = report_output.missing_info(inputdf=BSGW_output,
                                                  check_column='factuur naam',
                                                  verbose=True)


# In[45]:


output_filename = output_dir+ref_in_fname+"_"+retrieval_set_name+"_BSGW_output_TEMP"
#extended data output files
BSGW_output.to_csv(output_filename+".csv")
if output_to_excel and len(BSGW_output.index) < max_excel_lines: 
    BSGW_output.to_excel(output_filename+".xlsx",index=False)  


# In[46]:


output_filename = output_dir+ref_in_fname+"_"+retrieval_set_name+"_missing_billing_info"
#extended data output files
df_missing_billing.to_csv(output_filename+".csv")
if output_to_excel and len(df_missing_billing.index) < max_excel_lines: 
    df_missing_billing.to_excel(output_filename+".xlsx",index=False)  


# In[47]:


if full_verbose: display(BSGW_output.dtypes)


# In[48]:


# Set specific columns

#BSGW_output['local_time_min']=BSGW_output['local_time_min'].apply(str)
#BSGW_output['local_time_max']=BSGW_output['local_time_max'].apply(str)

# Only date is needed not time
BSGW_output['local_time_min']=BSGW_output['local_time_min'].dt.strftime('%Y-%m-%d')
BSGW_output['local_time_max']=BSGW_output['local_time_max'].dt.strftime('%Y-%m-%d')

BSGW_output['Naam']= BSGW_output['factuur naam']

BSGW_output['Subjectsoort']="R"
BSGW_output.loc[ BSGW_output["Landnaam"] != "" ,'Subjectsoort']="E"

BSGW_output['GEM. HEFSOORT']="NHAV"

BSGW_output['Subjectnr. ext']= BSGW_output['tonnage']

# de tekens: € / \ " ? ~ ` zijn niet toegestaan 
# maximale lengte 60 chars
BSGW_output['Omschrijving 1'] = BSGW_output['location_name'] + " / " + BSGW_output['name'] + " [" + BSGW_output['registratie-land'].str.replace(" ","") + "]" + " /ENI: " + BSGW_output['eni'] + " /Tonn: " + BSGW_output['tonnage']
        
BSGW_output['Omschrijving 1'] = BSGW_output['Omschrijving 1'].str.replace("€","Euro")
BSGW_output['Omschrijving 1'] = BSGW_output['Omschrijving 1'].str.replace("/",'-')
BSGW_output['Omschrijving 1'] = BSGW_output['Omschrijving 1'].str.replace("\\",'-')
BSGW_output['Omschrijving 1'] = BSGW_output['Omschrijving 1'].str.replace('"','')
BSGW_output['Omschrijving 1'] = BSGW_output['Omschrijving 1'].str.replace("?",'.')
BSGW_output['Omschrijving 1'] = BSGW_output['Omschrijving 1'].str.replace("~",'-')
BSGW_output['Omschrijving 1'] = BSGW_output['Omschrijving 1'].str.replace("`",'-')
BSGW_output['Omschrijving 1'] = BSGW_output['Omschrijving 1'].str.replace("Kade ",'')
BSGW_output['Omschrijving 1'] = BSGW_output['Omschrijving 1'].str.replace(" Born",'')
BSGW_output['Omschrijving 1'] = BSGW_output['Omschrijving 1'].str[0:58]

BSGW_output['Omschrijving 2'] = "van " + BSGW_output['local_time_min'] + " tot " + BSGW_output['local_time_max']
BSGW_output['Omschrijving 2'] = BSGW_output['Omschrijving 2'].str.replace("€",'Euro')
BSGW_output['Omschrijving 2'] = BSGW_output['Omschrijving 2'].str.replace("/",'-')
BSGW_output['Omschrijving 2'] = BSGW_output['Omschrijving 2'].str.replace("\\",'-')
BSGW_output['Omschrijving 2'] = BSGW_output['Omschrijving 2'].str.replace('"','')
BSGW_output['Omschrijving 2'] = BSGW_output['Omschrijving 2'].str.replace("?",'.')
BSGW_output['Omschrijving 2'] = BSGW_output['Omschrijving 2'].str.replace("~",'-')
BSGW_output['Omschrijving 2'] = BSGW_output['Omschrijving 2'].str.replace("`",'-')
BSGW_output['Omschrijving 2'] = BSGW_output['Omschrijving 2'].str[0:58]

BSGW_output['Omschrijving 3'] = ""

BSGW_output['Verblijfsduur'] = BSGW_output['time_diff_str']
BSGW_output['Verblijfsduur'] = BSGW_output['Verblijfsduur'].str.replace("0 days",'')
BSGW_output['Verblijfsduur'] = BSGW_output['Verblijfsduur'].str.replace("1 days",'1 dag')
BSGW_output['Verblijfsduur'] = BSGW_output['Verblijfsduur'].str.replace("days",'dagen')
BSGW_output['Verblijfsduur'] = BSGW_output['Verblijfsduur'].str.replace("€",'Euro')
BSGW_output['Verblijfsduur'] = BSGW_output['Verblijfsduur'].str.replace("/",'-')
BSGW_output['Verblijfsduur'] = BSGW_output['Verblijfsduur'].str.replace("\\",'-')
BSGW_output['Verblijfsduur'] = BSGW_output['Verblijfsduur'].str.replace('"','')
BSGW_output['Verblijfsduur'] = BSGW_output['Verblijfsduur'].str.replace("?",'.')
BSGW_output['Verblijfsduur'] = BSGW_output['Verblijfsduur'].str.replace("~",'-')
BSGW_output['Verblijfsduur'] = BSGW_output['Verblijfsduur'].str.replace("`",'-')
BSGW_output['Verblijfsduur'] = BSGW_output['Verblijfsduur'].str[0:58]

BSGW_output['MMSI-info'] = BSGW_output['mmsi']


# In[49]:


current_columns=list(BSGW_output.columns)

#CREATE OUTPUT
columns_to_write=['Naam','Voorletters','Voorvoegsel','Voornaam','Geslacht',
                'Burgersservicenr.','A-nummer','Handels - KVK-nr','Subjectsoort',
                'Geboortedatum','Banknr','Gironummer','Soort Adres','Datum Ingang Adres',
                'datum Einde Adres','Straat','Huisnr.','Postcode numeriek','Postcode alfanumeriek',
                'Postbusnr.','Huisletter','Toevoeging huisnr.','Aanduiding','Woonplaats','Buit. Adres 1',
                'Buit. Adres 2','Buit. Adres 3','Buit. Adres 4','Landnaam','Datum Overlijden',
                'BSN/Sofinr. Extra','Iban.rek.nr.','Bic-code','Subjectnr. ext','Vorderingnr.',
                'Heffingsjaar', 'Dagtekening','Bedrag incl.BTW','GEM. HEFSOORT','Bedrag excl.BTW',
                'Bedrag BTW','Omschrijving 1','Omschrijving 2','Omschrijving 3','LEEG','Verblijfsduur','MMSI-info']

#ADD MISSING COLUMNS
columns_to_add=set(list(columns_to_write))-set(list(current_columns))
BSGW_output = pd.concat([ BSGW_output , pd.DataFrame(columns=columns_to_add)],sort=False)  

#Sort on Omschrijving1, Omschrijving3 columns

BSGW_output.sort_values(['Omschrijving 1', 'Omschrijving 2'], ascending=[True, True], inplace=True)


# In[50]:


output_filename = output_dir+ref_in_fname+"_"+retrieval_set_name+"_BSGW_output"
#extended data output files
BSGW_output.to_csv(output_filename+".csv", columns=columns_to_write, index=False)
if output_to_excel and len(df_missing_billing.index) < max_excel_lines: 
    BSGW_output.to_excel(output_filename+".xlsx",columns=columns_to_write, index=False)


# In[51]:


#####################
#
# SAVE TO SERVER(S)
#
#####################


# In[52]:


#sftp stuff
import pysftp
import json


# In[53]:


# Read settings from json file 
with open(settings_dir+'settings.json', 'r') as jsonf: 
    SETTINGS = json.load(jsonf)
    #display(SETTINGS['sftpservers'])


# In[54]:


# loop trough all the servers whare data should be stored
for sftpserver in SETTINGS['sftpservers']:
    #display(SETTINGS['sftpservers'][sftpserver])
    #settings for sftp access
    sftp_host=SETTINGS['sftpservers'][sftpserver]['host']
    sftp_user=SETTINGS['sftpservers'][sftpserver]['user']
    sftp_pass=SETTINGS['sftpservers'][sftpserver]['password']
    #display(sftp_pass)
    
    display('exporting data to: '+sftpserver)
    ## GEOJSON INFO
    filename = ref_in_fname+"_BB_"+retrieval_set_name   
    remote_folder= str(yearfolder)+ "/" + municipality.lower() + "/geojson/" 

    #  transfer the files for the municipality
    with pysftp.Connection(host=sftp_host,username=sftp_user, password=sftp_pass) as sftp:
        print("Connection established")
        if not sftp.exists(remote_folder):
            print("creating remote folder: "+remote_folder)
            print("on host: "+sftp_host)
            print("as user: "+sftp_user)
            sftp.makedirs(remote_folder, mode=777)

        sftp.put(output_dir+filename+".geojson",remote_folder+filename+".geojson")

    ## AIS INFO
    filename = ref_in_fname+"_"+retrieval_set_name+"_AIS_extended"   
    remote_folder= str(yearfolder)+ "/" + municipality.lower() + "/ais/" 

    #  transfer the files for the municipality
    with pysftp.Connection(host=sftp_host,username=sftp_user, password=sftp_pass) as sftp:
        print("Connection established")
        if not sftp.exists(remote_folder):
            print("creating remote folder: "+remote_folder)
            print("on host: "+sftp_host)
            print("as user: "+sftp_user)
            sftp.sftp.makedirs(remote_folder, mode=777)

        sftp.put(output_dir+filename+".xlsx",remote_folder+filename+".xlsx")
        sftp.put(output_dir+filename+".csv",remote_folder+filename+".csv")


    ## STATISTICS    
    filename = ref_in_fname+"_"+retrieval_set_name+"_statistics_output"    
    remote_folder= str(yearfolder)+ "/" + municipality.lower() + "/beleid/" 

    #  transfer the files for the municipality
    with pysftp.Connection(host=sftp_host,username=sftp_user, password=sftp_pass) as sftp:
        print("Connection established")
        if not sftp.exists(remote_folder):
            print("creating remote folder: "+remote_folder)
            print("on host: "+sftp_host)
            print("as user: "+sftp_user)
            sftp.sftp.makedirs(remote_folder, mode=777)

        sftp.put(output_dir+filename+".xlsx",remote_folder+filename+".xlsx")
        sftp.put(output_dir+filename+".csv",remote_folder+filename+".csv")


    ## FINANCIAL
    filename = ref_in_fname+"_"+retrieval_set_name+"_BSGW_output"
    remote_folder= str(yearfolder)+ "/" + municipality.lower() + "/financieel/" 

    #  transfer the files for the municipality
    with pysftp.Connection(host=sftp_host,username=sftp_user, password=sftp_pass) as sftp:
        print("Connection established")
        if not sftp.exists(remote_folder):
            print("creating remote folder: "+remote_folder)
            print("on host: "+sftp_host)
            print("as user: "+sftp_user)
            sftp.sftp.makedirs(remote_folder, mode=777)

        sftp.put(output_dir+filename+".xlsx",remote_folder+filename+".xlsx")
        sftp.put(output_dir+filename+".csv",remote_folder+filename+".csv")
    
    


# In[55]:


display("DONE")


# In[ ]:




