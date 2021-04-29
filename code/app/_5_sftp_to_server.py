#from IPython.core.display import display

# basic stuff
import os
import json

# sftp stuff
import pysftp

settingsfile = "projectsettings.json"
# Read settings from json file
with open(settingsfile, 'r') as jsonf:
    SETTINGS = json.load(jsonf)

retrieval_set_name = SETTINGS['filenames']["retrieval_set_name"]
ref_in_fname = SETTINGS['filenames']["ref_in_fname"]  # used as reference in output filename

# folders for output
ref_dir = SETTINGS['folders']["ref_dir"]

# folders for output
output_dir = SETTINGS['folders']["output_dir"]

# folder for settings
settings_dir = SETTINGS['folders']["settings_dir"]

# debugging
full_verbose = SETTINGS['debug']["full_verbose"]

# Save statistics data, needed for SFTP
yearfolder = SETTINGS['output']["yearfolder"]
municipality = SETTINGS['output']["municipality"]

#####################
#
# SAVE TO SERVER(S)
#
#####################

# Read sftp settings from json file
with open(settings_dir+'settings.json', 'r') as jsonf: 
    SFTP_SETTINGS = json.load(jsonf)
    # print(SETTINGS['sftpservers'])

# loop trough all the servers whare data should be stored
for sftpserver in SFTP_SETTINGS['sftpservers']:
    # print(SETTINGS['sftpservers'][sftpserver])
    # settings for sftp access
    sftp_host = SFTP_SETTINGS['sftpservers'][sftpserver]['host']
    sftp_user = SFTP_SETTINGS['sftpservers'][sftpserver]['user']
    sftp_pass = SFTP_SETTINGS['sftpservers'][sftpserver]['password']
    # print(sftp_pass)
    
    print('exporting data to: '+sftpserver)

    # # GEOJSON INFO
    filename = ref_in_fname+"_BB_"+retrieval_set_name   
    remote_folder = str(yearfolder) + "/" + municipality.lower() + "/geojson/"

    try:
        #  transfer the files for the municipality
        with pysftp.Connection(host=sftp_host, username=sftp_user, password=sftp_pass) as sftp:
            print("Connection established")
            if not sftp.exists(remote_folder):
                print("creating remote folder: "+remote_folder)
                print("on host: "+sftp_host)
                print("as user: "+sftp_user)
                sftp.makedirs(remote_folder, mode=777)

            print("Sending to: " + sftpserver + ' server: /' + remote_folder)
            sftp.put(output_dir+filename+".geojson", remote_folder+filename+".geojson")
    except Exception as e:
        print(e)
        pass

    # # AIS INFO
    filename = ref_in_fname + "_" + retrieval_set_name+"_AIS_extended"
    remote_folder = str(yearfolder) + "/" + municipality.lower() + "/ais/"

    try:
        #  transfer the files for the municipality
        with pysftp.Connection(host=sftp_host, username=sftp_user, password=sftp_pass) as sftp:
            print("Connection established")
            if not sftp.exists(remote_folder):
                print("creating remote folder: "+remote_folder)
                print("on host: "+sftp_host)
                print("as user: "+sftp_user)
                sftp.sftp.makedirs(remote_folder, mode=777)

            print("Sending to: " + sftpserver + ' server: /' + remote_folder)
            sftp.put(output_dir+filename+".xlsx", remote_folder+filename+".xlsx")
            sftp.put(output_dir+filename+".csv", remote_folder+filename+".csv")
    except Exception as e:
        print(e)
        pass


    # # STATISTICS
    filename = ref_in_fname + "_" + retrieval_set_name + "_statistics_output"
    remote_folder = str(yearfolder) + "/" + municipality.lower() + "/beleid/"

    try:
        #  transfer the files for the municipality
        with pysftp.Connection(host=sftp_host, username=sftp_user, password=sftp_pass) as sftp:
            print("Connection established")
            if not sftp.exists(remote_folder):
                print("creating remote folder: "+remote_folder)
                print("on host: "+sftp_host)
                print("as user: "+sftp_user)
                sftp.sftp.makedirs(remote_folder, mode=777)

            print("Sending to: " + sftpserver + ' server: /' + remote_folder)
            sftp.put(output_dir+filename+".xlsx", remote_folder + filename+".xlsx")
            sftp.put(output_dir+filename+".csv", remote_folder + filename+".csv")
    except Exception as e:
        print(e)
        pass

    # # FINANCIAL
    filename = ref_in_fname + "_" + retrieval_set_name + "_BSGW_output"
    remote_folder = str(yearfolder) + "/" + municipality.lower() + "/financieel/"

    try:
        #  transfer the files for the municipality
        with pysftp.Connection(host=sftp_host, username=sftp_user, password=sftp_pass) as sftp:
            print("Connection established")
            if not sftp.exists(remote_folder):
                print("creating remote folder: "+remote_folder)
                print("on host: "+sftp_host)
                print("as user: "+sftp_user)
                sftp.sftp.makedirs(remote_folder, mode=777)

            print("Sending to: " + sftpserver + ' server: /' + remote_folder)
            sftp.put(output_dir+filename+".xlsx", remote_folder + filename + ".xlsx")
            sftp.put(output_dir+filename+".csv", remote_folder + filename + ".csv")
    except Exception as e:
        print(e)
        pass
