@ECHO off
SETLOCAL ENABLEEXTENSIONS

:: BASIC SETTINGS
:: ==============
:: Setting the name of the script
SET ME=%~n0
:: Setting the name of the directory
SET PARENT=%~p0
SET PDRIVE=%~d0

SET ERROR_MESSAGE=No error

:: set python / conda environment
IF EXIST .\_conda_environment.txt (
	SET /p conda_environment=<.\_conda_environment.txt
)
IF "%conda_environment%" == "" (
	SET ERROR_MESSAGE=[ERROR] file _conda_environment.txt does not exist or is empty ...
	GOTO :ERROR_EXIT
)

IF "%COMPUTERNAME%"=="LAPTOP2017"      GOTO :LAPTOP2017
IF "%COMPUTERNAME%"=="LEGION-2020"     GOTO :LEGION-2020

:Default
SET ERROR_MESSAGE=[ERROR] Unknown settings for COMPUTERNAME: %COMPUTERNAME% ...
GOTO :ERROR_EXIT

:LAPTOP2017
IF "%USERNAME%"=="pierr" (
   echo [INFO ] Commands for %USERNAME% on %COMPUTERNAME% ...
   echo [INFO ] Updating Conda ...
   call C:\myPrograms\anaconda3\Scripts\activate.bat
   call conda update -y -n base -c defaults conda
   GOTO :CLEAN_EXIT
)
IF "%USERNAME%"=="pierr_8jj0nf8" (
   echo [INFO ] Commands for %USERNAME% on %COMPUTERNAME% ...
   echo [INFO ] Updating Conda ...
   call C:\myPrograms\anaconda3\Scripts\activate.bat
   call conda update -y -n base -c defaults conda
   GOTO :CLEAN_EXIT
)
IF "%USERNAME%"=="myAdm" (
   echo [INFO ] Commands for %USERNAME% on %COMPUTERNAME% ...
   echo [INFO ] Updating Conda ...
   call C:\myPrograms\anaconda3\Scripts\activate.bat
   call conda update -y -n base -c defaults conda
   GOTO :CLEAN_EXIT
)
SET ERROR_MESSAGE=[ERROR] Not a valid user (%USERNAME%) on %COMPUTERNAME% ...
GOTO :ERROR_EXIT

:LEGION-2020
IF "%USERNAME%"=="developer" (
   echo [INFO ] Commands for %USERNAME% on %COMPUTERNAME% ...
   echo [INFO ] Updating Conda ...
   call C:\myPrograms\anaconda3\Scripts\activate.bat
   call conda update -y -n base -c defaults conda
   GOTO :CLEAN_EXIT
)
IF "%USERNAME%"=="myAdm" (
   echo [INFO ] Commands for %USERNAME% on %COMPUTERNAME% ...
   echo [INFO ] Updating Conda ...
   call C:\myPrograms\anaconda3\Scripts\activate.bat
   call conda update -y -n base -c defaults conda
   GOTO :CLEAN_EXIT
)
SET ERROR_MESSAGE=[ERROR] Not a valid user (%USERNAME%) on %COMPUTERNAME% ...
GOTO :ERROR_EXIT

:ERROR_EXIT
ECHO %ERROR_MESSAGE%

:CLEAN_EXIT

PAUSE
