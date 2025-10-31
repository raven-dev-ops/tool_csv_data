@echo off
setlocal

REM Build MamboLite CLI and GUI as Windows executables using PyInstaller

where pyinstaller >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
  echo Installing PyInstaller...
  pip install pyinstaller || goto :error
)

echo Building CLI...
python -m PyInstaller --noconfirm --onefile MamboLite\mambo_lite.py ^
  --add-data "MamboLite\lookups;lookups" ^
  --add-data "MamboLite\smtp.json.example;." ^
  --name MamboLiteCLI || goto :error

echo Building GUI...
python -m PyInstaller --noconfirm --onefile --windowed MamboLite\mambo_lite_gui.py ^
  --add-data "MamboLite\lookups;lookups" ^
  --add-data "MamboLite\smtp.json.example;." ^
  --name MamboLite || goto :error

echo Done. Executables are in the dist folder.
exit /b 0

:error
echo Build failed.
exit /b 1
