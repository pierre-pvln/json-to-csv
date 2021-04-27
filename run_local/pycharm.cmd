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

:: set python / conda environment
SET conda_environment=py3.8-datascience

:: goto to correct startpoint/directory for the IDE
CD ..
SET "IDE_START_DIR=%CD%"

IF "%COMPUTERNAME%"=="LAPTOP2017"      GOTO :LAPTOP2017
IF "%COMPUTERNAME%"=="LEGION-2020"     GOTO :LEGION-2020

:Default
ECHO ERROR: Unknown settings for COMPUTERNAME: %COMPUTERNAME%
GOTO :DONE

:LAPTOP2017
IF "%USERNAME%"=="pierr" (
   echo Running PyCharm IDE for %USERNAME% on %COMPUTERNAME%
   call C:\myPrograms\anaconda3\Scripts\activate.bat
   call conda activate %conda_environment%
   cd .\code
   call "C:\Program Files\JetBrains\PyCharm Community Edition 2020.2.2\bin\pycharm64.exe" %IDE_START_DIR%
   cd ..
   GOTO :DONE
)
IF "%USERNAME%"=="pierr_8jj0nf8" (
   echo Running PyCharm IDE for %USERNAME% on %COMPUTERNAME%
   call C:\myPrograms\anaconda3\Scripts\activate.bat
   call conda activate %conda_environment%
   cd .\code
   call "C:\Program Files\JetBrains\PyCharm Community Edition 2020.2.2\bin\pycharm64.exe" %IDE_START_DIR%
   cd ..
   GOTO :DONE
)
ECHO Not a valid user (%USERNAME%) on %COMPUTERNAME%
GOTO :DONE

:LEGION-2020
IF "%USERNAME%"=="developer" (
   echo Running PyCharm IDE for %USERNAME% on %COMPUTERNAME%
   call C:\myPrograms\anaconda3\Scripts\activate.bat
   call conda activate %conda_environment%
   cd .\code
   call "C:\Program Files\JetBrains\PyCharm Community Edition 2020.2.2\bin\pycharm64.exe" %IDE_START_DIR%
   cd ..
   GOTO :DONE
)
IF "%USERNAME%"=="pierre" (
   echo Running PyCharm IDE for %USERNAME% on %COMPUTERNAME%
   call C:\myPrograms\anaconda3\Scripts\activate.bat
   call conda activate %conda_environment%
   cd .\code
   call "C:\Program Files\JetBrains\PyCharm Community Edition 2020.2.2\bin\pycharm64.exe" %IDE_START_DIR%
   cd ..
   GOTO :DONE
)
ECHO Not a valid user (%USERNAME%) on %COMPUTERNAME%
GOTO :DONE

:DONE
CD %CMD_DIR%
PAUSE