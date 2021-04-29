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
   echo commands for %USERNAME% on %COMPUTERNAME%
   call C:\myPrograms\anaconda3\Scripts\activate.bat
   call conda activate %conda_environment%
   call conda env list
   call conda list
   echo going to install awswrangler
   pause
   call conda install -c conda-forge awswrangler 
   GOTO :CLEAN_EXIT
)
IF "%USERNAME%"=="pierr_8jj0nf8" (
   echo commands for %USERNAME% on %COMPUTERNAME%
   call C:\myPrograms\anaconda3\Scripts\activate.bat
   call conda activate %conda_environment%
   call conda env list
   call conda list
   echo going to install awswrangler
   pause
   call conda install -c conda-forge awswrangler
   GOTO :CLEAN_EXIT
)
IF "%USERNAME%"=="myAdm" (
   echo commands for %USERNAME% on %COMPUTERNAME%
   call C:\myPrograms\anaconda3\Scripts\activate.bat
   call conda activate %conda_environment%
   call conda env list
   call conda list
   echo going to install awswrangler
   pause
   call conda install -c conda-forge awswrangler
   GOTO :CLEAN_EXIT
)
SET ERROR_MESSAGE=[ERROR] Not a valid user (%USERNAME%) on %COMPUTERNAME% ...
GOTO :ERROR_EXIT

:LEGION-2020
IF "%USERNAME%"=="developer" (
   echo [INFO ] Commands for %USERNAME% on %COMPUTERNAME% ...
   echo [INFO ] Installing python 3.8 ...
   call C:\myPrograms\anaconda3\Scripts\activate.bat
   call conda create -y --name %conda_environment% python=3.8
   call C:\myPrograms\anaconda3\Scripts\activate.bat
   call conda activate %conda_environment%
   cls
   echo.
   echo [INFO ] Installing rtree ...
   echo.
   call conda install -y -c conda-forge rtree
   TIMEOUT /T 2
   CLS
   echo.
   echo [INFO ] Installing shapely ...
   echo.
   call conda install -y -c conda-forge shapely
   TIMEOUT /T 2
   CLS
   echo.
   echo [INFO ] Installing geopandas ...
   echo.
   call conda install -y -c conda-forge geopandas
   TIMEOUT /T 2
   CLS
   echo.
   echo [INFO ] Installing pandas ...
   echo.
   call conda install -y -c anaconda pandas
   TIMEOUT /T 2
   CLS
   echo.
   echo [INFO ] Installing openpyxl ...
   echo.
   call  conda install -y -c anaconda openpyxl  
   TIMEOUT /T 2
   CLS
   echo.
   echo [INFO ] Installing boto3 ...
   echo.
   call conda install -y -c anaconda boto3
   TIMEOUT /T 2
   CLS
   echo.
   echo [INFO ] Installing awswrangler ...
   echo.
   call conda install -y -c conda-forge awswrangler
   TIMEOUT /T 2
   CLS
   echo.
   echo [INFO ] Installing pysftp ...
   echo.
   call conda install -y -c conda-forge pysftp
   TIMEOUT /T 2
   CLS
   call conda env list
   echo.
   GOTO :CLEAN_EXIT
)
IF "%USERNAME%"=="myAdm" (
   echo commands for %USERNAME% on %COMPUTERNAME%
   call C:\myPrograms\anaconda3\Scripts\activate.bat
   call conda activate %conda_environment%
   call conda env list
   call conda list
   echo going to install awswrangler
   pause
   call conda install -c conda-forge awswrangler
   GOTO :CLEAN_EXIT
)
SET ERROR_MESSAGE=[ERROR] Not a valid user (%USERNAME%) on %COMPUTERNAME% ...
GOTO :ERROR_EXIT

:ERROR_EXIT
ECHO %ERROR_MESSAGE%

:CLEAN_EXIT

PAUSE
