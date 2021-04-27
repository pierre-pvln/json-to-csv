:: Name:     copy_settings_to_s3.cmd
:: Purpose:  Copy all relevant settings files to S3 bucket
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

:: https://docs.aws.amazon.com/lambda/latest/dg/python-package.html
::

:: create zip file
"C:\Program Files\7-Zip\7z.exe" a -tzip "my-deployment-package.zip" "..\code\lambda_function.py"

:: update lambda code
%AWS_cli% %CLI_Options_JSON% lambda update-function-code --function-name aishub-data-to-csv --zip-file fileb://my-deployment-package.zip


GOTO CLEAN_EXIT

:ERROR_EXIT
cd "%cmd_dir%" 
ECHO *******************
ECHO %ERROR_MESSAGE%
ECHO *******************

   
:CLEAN_EXIT   
:: Wait some time and exit the script
::
timeout /T 10