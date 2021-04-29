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

:: set python / conda environment
IF EXIST ".\conda modules\_conda_environment.txt" (
	SET /p conda_environment=<".\conda modules\_conda_environment.txt"
)

IF "%conda_environment%" == "" (
	SET ERROR_MESSAGE=[ERROR] file .\conda modules\_conda_environment.txt does not exist or is empty ...
	GOTO :ERROR_EXIT
)

:: set the correct settings for AWS
COPY .\aws_identities\ipheion_AWS-profile.txt ..\scripts\_AWS-profile.txt
COPY .\aws_identities\ipheion_AWS-region.txt ..\scripts\_AWS-region.txt

:: set any required environment variables
SET AWS_PROFILE_NAME=ipheion

:: set 'SPATIALINDEX_C_LIBRARY' otherwise rtree / geopandas complains
SET SPATIALINDEX_C_LIBRARY=C:/myPrograms/anaconda3/envs/%conda_environment%/Library/bin

:: start python script(s)
CALL run-python-script.cmd

GOTO :CLEAN_EXIT

:ERROR_EXIT
ECHO %ERROR_MESSAGE%

:CLEAN_EXIT
CD %CMD_DIR%

PAUSE
