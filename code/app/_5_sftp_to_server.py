# basic stuff
import os
import json
import socket

# sftp stuff
import paramiko

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


def sftp_makedirs(sftp_client, remote_directory):
    '''
    Recursively create remote_directory (and any missing parent folders)
    if it does not exist yet. paramiko has no built-in "makedirs".
    '''
    if remote_directory in ('', '/'):
        return
    try:
        sftp_client.stat(remote_directory)
        return  # already exists
    except FileNotFoundError:
        pass

    parent, _ = os.path.split(remote_directory.rstrip('/'))
    if parent and parent != remote_directory:
        sftp_makedirs(sftp_client, parent)

    try:
        sftp_client.mkdir(remote_directory)
    except OSError:
        # race condition / already created by something else in the meantime
        pass


def sftp_put_if_exists(sftp_client, local_path, remote_path):
    '''
    Upload local_path to remote_path if the local file exists.
    Prints a message and skips otherwise (mirrors old try/except/pass behaviour,
    but without silently swallowing real connection errors).
    '''
    if not os.path.exists(local_path):
        print("Skipping, local file not found: " + local_path)
        return
    print("Sending: " + local_path + "  ->  " + remote_path)
    sftp_client.put(local_path, remote_path)


#####################
# SAVE TO SERVER(S)
#####################

# Read sftp settings from json file
with open(settings_dir+'settings.json', 'r') as jsonf:
    SFTP_SETTINGS = json.load(jsonf)
    # print(SETTINGS['sftpservers'])

# loop through all the servers where data should be stored
for sftpserver in SFTP_SETTINGS['sftpservers']:
    # settings for sftp access
    sftp_host = SFTP_SETTINGS['sftpservers'][sftpserver]['host']
    sftp_user = SFTP_SETTINGS['sftpservers'][sftpserver]['user']
    sftp_pass = SFTP_SETTINGS['sftpservers'][sftpserver]['password']

    print('exporting data to: ' + sftpserver)

    transport = None
    try:
        transport = paramiko.Transport((sftp_host, 22))
        transport.connect(username=sftp_user, password=sftp_pass)
        sftp = paramiko.SFTPClient.from_transport(transport)
        print("Connection established")

        # GEOJSON INFO FILES
        # ==================
        # TODO not shure yet what to do with geojsons
        local_fname = ref_in_fname + "_" + the_hostname + "_BB_" + projectname
        remote_fname = ref_in_fname + "_BB_" + projectname
        remote_folder = str(yearfolder) + "/" + municipality.lower() + "/geojson/"

        sftp_makedirs(sftp, remote_folder)
        sftp_put_if_exists(sftp, output_dir + local_fname + ".geojson", remote_folder + remote_fname + ".geojson")

        # AIS INFO FILES
        # ==================
        local_fname = ref_in_fname + "_" + the_hostname + "_" + projectname + "_AIS_extended"
        remote_fname = ref_in_fname + "_" + projectname + "_AIS_extended"
        remote_folder = str(yearfolder) + "/" + municipality.lower() + "/ais/"

        sftp_makedirs(sftp, remote_folder)
        sftp_put_if_exists(sftp, output_dir + local_fname + ".xlsx", remote_folder + remote_fname + ".xlsx")
        sftp_put_if_exists(sftp, output_dir + local_fname + ".csv", remote_folder + remote_fname + ".csv")

        # STATISTICS FILES
        # ==================
        local_fname = ref_in_fname + "_" + the_hostname + "_" + projectname + "_statistics_output"
        remote_fname = ref_in_fname + "_" + the_hostname + "_" + projectname + "_statistics_output"
        remote_folder = str(yearfolder) + "/" + municipality.lower() + "/beleid/"

        sftp_makedirs(sftp, remote_folder)
        sftp_put_if_exists(sftp, output_dir + local_fname + ".xlsx", remote_folder + remote_fname + ".xlsx")
        sftp_put_if_exists(sftp, output_dir + local_fname + ".csv", remote_folder + remote_fname + ".csv")

        # FINANCIAL FILES
        # ==================
        local_fname = ref_in_fname + "_" + the_hostname + "_" + projectname + "_BSGW_output"
        remote_fname = ref_in_fname + "_" + projectname + "_BSGW_output"
        remote_folder = str(yearfolder) + "/" + municipality.lower() + "/financieel/"

        sftp_makedirs(sftp, remote_folder)
        sftp_put_if_exists(sftp, output_dir + local_fname + ".xlsx", remote_folder + remote_fname + ".xlsx")
        sftp_put_if_exists(sftp, output_dir + local_fname + ".csv", remote_folder + remote_fname + ".csv")

    except Exception as e:
        print(e)
    finally:
        if transport is not None:
            transport.close()
