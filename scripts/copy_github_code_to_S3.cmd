:: Name:     copy_github_code_to_s3.cmd
:: Purpose:  Copy files from github to S3 bucket
:: Author:   pierre@pvln.nl
::
:: Required environment variables
:: ==============================
::
:: NONE
::
@ECHO off
SETLOCAL ENABLEEXTENSIONS

:: BASIC SETTINGS
:: ==============
:: Setting the name of the script
SET me=%~n0
:: Setting the name of the directory with this script
SET parent=%~p0
:: Setting the drive of this commandfile
SET drive=%~d0
:: Setting the directory and drive of this commandfile
SET cmd_dir=%~dp0
::
:: (re)set environment variables
::
SET VERBOSE=YES
::
:: Setting for Error messages
::
SET ERROR_MESSAGE=errorfree

:: AWS SETTINGS
:: ============
:: 
SET AWS_cli=aws
IF "%COMPUTERNAME%"=="LAPTOP2017"      SET AWS_cli=aws2
IF "%COMPUTERNAME%"=="LEGION-2020"     SET AWS_cli=aws

SET /p AWS_region=<.\_AWS-region.txt
IF "%AWS_region%" == "" (
	SET AWS_region=eu-central-1
)

SET /p AWS_profile=<.\_AWS-profile.txt
IF "%AWS_profile%" == "" (
	SET AWS_profile=ipheion
)

SET CLI_Options_TEXT=--profile %AWS_profile% --region %AWS_region% --output text --color on
SET CLI_Options_TABLE=--profile %AWS_profile% --region %AWS_region% --output table --color on
SET CLI_Options_JSON=--profile %AWS_profile% --region %AWS_region% --output json --color on

:: create temp local file store
:: cleanup first
ECHO [INFO ] Clean up local ...
IF EXIST "..\S3_files\json-to-csv\" (RMDIR /S /Q "..\S3_files\json-to-csv\")

ECHO [INFO ] Clean up S3 ...
%AWS_cli% %CLI_Options_JSON% s3 rm s3://iph-code-repository/json-to-csv/ --recursive

IF NOT EXIST "..\S3_files\" (MKDIR "..\S3_files\")
CD "..\S3_files\"

ECHO [INFO ] Retrieving files from github ...
git clone git@github.com:pierre-pvln/json-to-csv.git json-to-csv

ECHO [INFO ] Copy files to S3 bucket ...
:: copy files to s3 bucket
::%AWS_cli% %CLI_Options_JSON% s3 cp ./json-to-csv s3://iph-code-repository/json-to-csv/ --exclude "*.git/*" --recursive --dryrun
%AWS_cli% %CLI_Options_JSON% s3 cp ./json-to-csv s3://iph-code-repository/json-to-csv/ --exclude "*.git/*" --recursive

GOTO CLEAN_EXIT

:ERROR_EXIT
CD "%cmd_dir%" 
ECHO *******************
ECHO %ERROR_MESSAGE%
ECHO *******************

   
:CLEAN_EXIT   
CD "%cmd_dir%" 
:: Wait some time and exit the script
::
timeout /T 10