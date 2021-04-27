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

:: set the correct settings for AWS
COPY .\aws_identities\ipheion_AWS-profile.txt ..\scripts\_AWS-profile.txt
COPY .\aws_identities\ipheion_AWS-region.txt ..\scripts\_AWS-region.txt

:: set any required environment variables
SET AWS_PROFILE_NAME=ipheion

:: set 'SPATIALINDEX_C_LIBRARY' otherwise rtree / geopandas complains
SET SPATIALINDEX_C_LIBRARY=C:/myPrograms/anaconda3/envs/py3.8-datascience/Library/bin

:: start IDE
CALL pycharm.cmd
