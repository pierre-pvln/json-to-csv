@ECHO off
SETLOCAL ENABLEEXTENSIONS

:: BASIC SETTINGS
:: ==============
:: Setting the name of the script
SET ME=%~n0
:: Setting the name of the directory
SET PARENT=%~p0
SET PDRIVE=%~d0
:: Setting the directory and drive of this commandfile
SET CMD_DIR=%~dp0

cd ..\code\app
SET continue=true

call C:\myPrograms\anaconda3\Scripts\activate.bat
call conda activate %conda_environment%

IF "%continue%"=="true" (
    echo "[INFO ] Running script 1"
    echo "[INFO ] ================"
    python _1_get_baseline.py
    if %ERRORLEVEL% NEQ 0 (
            SET continue=false
            SET ERROR_MESSAGE=[ERROR] Ending script
    )
)

IF "%continue%"=="true" (
    echo "[INFO ] Running script 2"
    echo "[INFO ] ================"
    python _2_extend_baseline.py
    if %ERRORLEVEL% NEQ 0 (
            SET continue=false
            SET ERROR_MESSAGE=[ERROR] Ending script
    )
)

IF "%continue%"=="true" (
    echo "[INFO ] Running script 3"
    echo "[INFO ] ================"
    python _3_statistics_output.py
    if %ERRORLEVEL% NEQ 0 (
            SET continue=false
            SET ERROR_MESSAGE=[ERROR] Ending script
    )
)

IF "%continue%"=="true" (
    echo "[INFO ] Running script 4"
    echo "[INFO ] ================"
    python _4_bsgw_format.py
    if %ERRORLEVEL% NEQ 0 (
            SET continue=false
			SET ERROR_MESSAGE=[ERROR] Ending script
    )
)

IF "%continue%"=="true" (
    echo "[INFO ] Running script 5"
    echo "[INFO ] ================"
    python _5_sftp_to_server.py
    if %ERRORLEVEL% NEQ 0 (
            SET continue=false
            SET ERROR_MESSAGE=[ERROR] Ending script
    )
)

conda deactivate
GOTO :CLEAN_EXIT

:ERROR_EXIT
ECHO %ERROR_MESSAGE%
conda deactivate

:CLEAN_EXIT
CD %CMD_DIR%

PAUSE
