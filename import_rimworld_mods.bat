@echo off
setlocal enabledelayedexpansion
REM Batch Import Script for RimWorld Mod Collections
REM This script imports all the specified RimWorld mod folders

echo ===============================================
echo RimWorld Mod Collections - Batch Import
echo ===============================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Define the base path and owner
set "BASE_PATH=C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods"
set "OWNER=ProgrammerLily"

echo Base path: %BASE_PATH%
echo Owner: %OWNER%
echo.

REM Define all the mod folders to import
set "MODS=WhatsWrong BetterPlanning BrushTool BuildFromStorage ComfortableFishing FishEggs FoodBowl HospitalityDoors LoadedTextureViewer OxygenSupply PrioritizedKillTool QuickDevBuild rimworld-tradingspot ShipVents WasteNotWantNot"

REM Count total mods
set /a MOD_COUNT=0
for %%m in (%MODS%) do set /a MOD_COUNT+=1

echo Found %MOD_COUNT% mods to import:
for %%m in (%MODS%) do echo   - %%m

echo.
echo This will create %MOD_COUNT% new collections in the Texture Reference Vault.
echo Each collection will be owned by: %OWNER%
echo.

REM Ask for confirmation
set /p CONFIRM="Proceed with batch import? (y/N): "
if /i not "%CONFIRM%"=="y" (
    if /i not "%CONFIRM%"=="yes" (
        echo Import cancelled.
        pause
        exit /b 0
    )
)

echo.
echo Starting batch import...
echo ===============================================

REM Import each mod
set /a CURRENT=0
for %%m in (%MODS%) do (
    set /a CURRENT+=1
    echo.
    echo [!CURRENT!/%MOD_COUNT%] Importing: %%m
    echo -----------------------------------------------
    
    REM Check if folder exists
    if exist "%BASE_PATH%\%%m" (
        python import_collection.py --folder "%BASE_PATH%\%%m" --name "RimWorld - %%m Mod" --owner "%OWNER%" --description "Textures and images from the %%m RimWorld mod" --yes
        
        if errorlevel 1 (
            echo WARNING: Import failed for %%m
            echo.
            set /p CONTINUE="Continue with remaining imports? (y/N): "
            if /i not "!CONTINUE!"=="y" (
                if /i not "!CONTINUE!"=="yes" (
                    echo Batch import stopped.
                    pause
                    exit /b 1
                )
            )
        ) else (
            echo SUCCESS: %%m imported successfully
        )
    ) else (
        echo WARNING: Folder not found: %BASE_PATH%\%%m
    )
)

echo.
echo ===============================================
echo Batch import completed!
echo ===============================================
echo.
echo Check the results above for any errors or warnings.
pause
