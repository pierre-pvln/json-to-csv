@ECHO off
SETLOCAL ENABLEEXTENSIONS

:: BASIC SETTINGS
:: ==============
:: Setting the name of the script
SET ME=%~n0
:: Setting the name of the directory
SET PARENT=%~p0
SET PDRIVE=%~d0

:: set python / conda environment
SET conda_environment=py3.8-datascience

IF "%COMPUTERNAME%"=="LAPTOP2017"      GOTO :LAPTOP2017
IF "%COMPUTERNAME%"=="LEGION-2020"     GOTO :LEGION-2020

:Default
ECHO ERROR: Unknown settings for COMPUTERNAME: %COMPUTERNAME%
GOTO :DONE

:Personal_laptop
IF "%USERNAME%"=="pierr" (
   echo commands for %USERNAME% on %COMPUTERNAME%
   call C:\myPrograms\anaconda3\Scripts\activate.bat
   call conda activate %conda_environment%
   call conda env list
   call conda list
   echo going to install awswrangler
   pause
   call conda install -c conda-forge awswrangler 
   GOTO :DONE
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
   GOTO :DONE
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
   GOTO :DONE
)
ECHO Not a valid user (%USERNAME%) on %COMPUTERNAME%
GOTO :DONE


:LEGION-2020
IF "%USERNAME%"=="developer" (
   echo commands for %USERNAME% on %COMPUTERNAME%
   call C:\myPrograms\anaconda3\Scripts\activate.bat
   call conda activate %conda_environment%
   call conda env list
   call conda list
   echo going to install awswrangler
   pause
   call conda install -c conda-forge awswrangler
   GOTO :DONE
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
   GOTO :DONE
)
ECHO Not a valid user (%USERNAME%) on %COMPUTERNAME%
GOTO :DONE



:DONE
Pause