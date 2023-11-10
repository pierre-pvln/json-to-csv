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

SET ERROR_MESSAGE=[INFO ] No error

SET "CONDA_CONF_PATH=.\"
SET "CONDA_ENV_NAME_FILE=%CONDA_CONF_PATH%_conda_environment.txt"
SET "CONDA_CONF_YML_FILE=%CONDA_CONF_PATH%environment.yml"

:: set python / conda environment name
IF EXIST %CONDA_ENV_NAME_FILE% (
	SET /p conda_environment=<%CONDA_ENV_NAME_FILE%
)
IF "%conda_environment%" == "" (
	SET ERROR_MESSAGE=[ERROR] file %CONDA_ENV_NAME_FILE% does not exist or is empty ...
	GOTO ERROR_EXIT
)

:: set python / conda environment yml file
IF NOT EXIST %CONDA_ENV_NAME_FILE% (
	SET ERROR_MESSAGE=[ERROR] file %CONDA_ENV_NAME_FILE% does not exist ...
	GOTO ERROR_EXIT
)

IF "%COMPUTERNAME%"=="LEGION-2020"     GOTO :LEGION-2020

:Default
SET ERROR_MESSAGE=[ERROR] Unknown settings for COMPUTERNAME: %COMPUTERNAME% ...
GOTO ERROR_EXIT

:LEGION-2020
IF "%USERNAME%"=="developer" (
   echo [INFO ] Commands for %USERNAME% on %COMPUTERNAME% ...
   call C:\myPrograms\anaconda3\Scripts\activate.bat
   echo [INFO ] Exporting conda environment %conda_environment% ...
   call conda env export --name %conda_environment% --no-builds > conda_env_as-built.yml
   GOTO CLEAN_EXIT
)

IF "%USERNAME%"=="myAdm" (
   echo [INFO ] Commands for %USERNAME% on %COMPUTERNAME% ...
   call C:\myPrograms\anaconda3\Scripts\activate.bat
   echo [INFO ] Exporting conda environment %conda_environment% ...
   call conda env export --name %conda_environment% --no-builds > conda_env_as-built.yml
   GOTO CLEAN_EXIT
)

SET ERROR_MESSAGE=[ERROR] Not a valid user (%USERNAME%) on %COMPUTERNAME% ...
GOTO ERROR_EXIT

:ERROR_EXIT
ECHO %ERROR_MESSAGE%

:CLEAN_EXIT
CD %CMD_DIR%
timeout /t 5
