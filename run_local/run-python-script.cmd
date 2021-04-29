cd ..\json-to-csv\code\app

:: set python / conda environment
IF EXIST ".\conda modules\_conda_environment.txt" (
	SET /p conda_environment=<".\conda modules\_conda_environment.txt"
)
IF "%conda_environment%" == "" (
	SET ERROR_MESSAGE=[ERROR] file .\conda modules\_conda_environment.txt does not exist or is empty ...
	GOTO :ERROR_EXIT
)

SET continue=true

call C:\myPrograms\anaconda3\Scripts\activate.bat
call conda activate %conda_environment%

IF "%continue%"=="true" (
    echo "[INFO ] Running script 1"
    echo "[INFO ] ================"
    python3 _1_get_baseline.py
    if %ERRORLEVEL% NEQ 0 (
            SET continue=false
            echo "[ERROR] Ending script"
    )
)

IF "%continue%"=="true" (
    echo "[INFO ] Running script 2"
    echo "[INFO ] ================"
    python3 _2_extend_baseline.py
    if %ERRORLEVEL% NEQ 0 (
            SET continue=false
            echo "[ERROR] Ending script"
    )
)

IF "%continue%"=="true" (
    echo "[INFO ] Running script 3"
    echo "[INFO ] ================"
    python3 _3_statistics_output.py
    if %ERRORLEVEL% NEQ 0 (
            SET continue=false
            echo "[ERROR] Ending script"
    )
)

IF "%continue%"=="true" (
    echo "[INFO ] Running script 4"
    echo "[INFO ] ================"
    python3 _4_bsgw_format.py
    if %ERRORLEVEL% NEQ 0 (
            SET continue=false
            echo "[ERROR] Ending script"
    )
)

IF "%continue%"=="true" (
    echo "[INFO ] Running script 5"
    echo "[INFO ] ================"
    python3 _5_sftp_to_server.py
    if %ERRORLEVEL% NEQ 0 (
            SET continue=false
            echo "[ERROR] Ending script"
    )
)

deactivate

cd ..\json-to-csv\code\app

:ERROR_EXIT
ECHO %ERROR_MESSAGE%

:CLEAN_EXIT

PAUSE
