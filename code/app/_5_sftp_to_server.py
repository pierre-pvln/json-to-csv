# basic stuff
import json
import socket

# sftp stuff
import pysftp

settingsfile = "projectsettings.json"
# Read settings from json file
with open(settingsfile, 'r') as jsonf:
    SETTINGS = json.load(jsonf)

projectname = SETTINGS['project']['name']

ref_in_fname = SETTINGS['filenames']["ref_in_fname"]  # used as reference in output filename

# folders for output
output_dir = SETTINGS['folders']["output_dir"]

# folder for settings
settings_dir = SETTINGS['folders']["settings_dir"]

# debugging
full_verbose = SETTINGS['debug']["full_verbose"]

# Save statistics data, needed for SFTP
yearfolder = SETTINGS['output']["yearfolder"]
municipality = SETTINGS['output']["municipality"]

the_hostname = socket.gethostname()
print('running on   : '+the_hostname)

#####################
# SAVE TO SERVER(S)
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

    # GEOJSON INFO FILES
    # ==================
    #
    # TODO not shure yet what to do with geojsons
    #
    local_fname = ref_in_fname + "_" + the_hostname + "_BB_" + projectname
    remote_fname = ref_in_fname + "_BB_" + projectname
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
            sftp.put(output_dir + local_fname + ".geojson", remote_folder + remote_fname + ".geojson")
    except Exception as e:
        print(e)
        pass

    # AIS INFO FILES
    # ==================
    local_fname = ref_in_fname + "_" + the_hostname + "_" + projectname + "_AIS_extended"
    remote_fname = ref_in_fname + "_" + projectname + "_AIS_extended"
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
            sftp.put(output_dir + local_fname + ".xlsx", remote_folder + remote_fname + ".xlsx")
            sftp.put(output_dir + local_fname + ".csv", remote_folder + remote_fname + ".csv")
    except Exception as e:
        print(e)
        pass

    # STATISTICS FILES
    # ==================
    local_fname = ref_in_fname + "_" + the_hostname + "_" + projectname + "_statistics_output"
    remote_fname = ref_in_fname + "_" + the_hostname + "_" + projectname + "_statistics_output"
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
            sftp.put(output_dir + local_fname + ".xlsx", remote_folder + remote_fname + ".xlsx")
            sftp.put(output_dir + local_fname + ".csv", remote_folder + remote_fname + ".csv")
    except Exception as e:
        print(e)
        pass

    # FINANCIAL FILES
    # ==================
    local_fname = ref_in_fname + "_" + the_hostname + "_" + projectname + "_BSGW_output"
    remote_fname = ref_in_fname + "_" + projectname + "_BSGW_output"
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
            sftp.put(output_dir + local_fname + ".xlsx", remote_folder + remote_fname + ".xlsx")
            sftp.put(output_dir + local_fname + ".csv", remote_folder + remote_fname + ".csv")
    except Exception as e:
        print(e)
        pass
