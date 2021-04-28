#!/usr/bin/env bash
# https://stackoverflow.com/questions/13086109/check-if-bash-variable-equals-0
#
cd ~/json-to-csv/code/app

touch $( date '+%Y-%m-%d_%H-%M-%S' )_app_started
source ~/env/bin/activate

continue=true

if [[ "${continue}" == "true" ]]
then
    echo "[INFO ] Running script 1"
    echo "[INFO ] ================"
    python3 _1_get_baseline.py
    if [[ $? -ne 0 ]]
        then
            continue=false
            echo "[ERROR] Ending script"
    fi
fi

if [[ "${continue}" == "true" ]]
then
    echo "[INFO ] Running script 2"
    echo "[INFO ] ================"
    python3 _2_extend_baseline.py
    if [[ $? -ne 0 ]]
        then
            continue=false
            echo "[ERROR] Ending script"
    fi
fi

if [[ "${continue}" == "true" ]]
then
    echo "[INFO ] Running script 3"
    echo "[INFO ] ================"
    python3 _3_statistics_output.py
    if [[ $? -ne 0 ]]
        then
            continue=false
            echo "[ERROR] Ending script"
    fi
fi

if [[ "${continue}" == "true" ]]
then
    echo "[INFO ] Running script 4"
    echo "[INFO ] ================"
    python3 _4_bsgw_format.py
    if [[ $? -ne 0 ]]
        then
            continue=false
            echo "[ERROR] Ending script"
    fi
fi

if [[ "${continue}" == "true" ]]
then
    echo "[INFO ] Running script 5"
    echo "[INFO ] ================"
    python3 _5_sftp_to_server.py
    if [[ $? -ne 0 ]]
        then
            continue=false
            echo "[ERROR] Ending script"
    fi
fi

deactivate

cd ~/json-to-csv/code/app
touch $( date '+%Y-%m-%d_%H-%M-%S' )_app_ended
