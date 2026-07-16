@echo off
REM Refresh bundled binaries from your Desktop build folders (slim copy ??? no CUDA toolkit).
title Sync TrueNexus tools
cd /d "%~dp0"

set "SRC_TC=D:\TrueScent\TrueCollider"
set "SRC_MK=D:\TrueScent\TrueMkeyCollider"
set "DST_TC=%~dp0tools\TrueCollider"
set "DST_MK=%~dp0tools\TrueMkeyCollider"

if not exist "%SRC_TC%\keyhunt.exe" (
  echo [E] Missing %SRC_TC%\keyhunt.exe
  echo     Edit SRC_TC in this bat if your collider lives elsewhere.
  pause
  exit /b 1
)
if not exist "%SRC_MK%\TrueMkeyCollider.exe" (
  echo [E] Missing %SRC_MK%\TrueMkeyCollider.exe
  pause
  exit /b 1
)

mkdir "%DST_TC%" 2>nul
mkdir "%DST_MK%" 2>nul

echo [+] Syncing TrueCollider runtime...
copy /Y "%SRC_TC%\keyhunt.exe" "%DST_TC%\" >nul
if exist "%SRC_TC%\keyhunt_cuda.exe" copy /Y "%SRC_TC%\keyhunt_cuda.exe" "%DST_TC%\" >nul
if exist "%SRC_TC%\run_keyhunt.bat" copy /Y "%SRC_TC%\run_keyhunt.bat" "%DST_TC%\" >nul
if exist "%SRC_TC%\README.md" copy /Y "%SRC_TC%\README.md" "%DST_TC%\" >nul
if exist "%SRC_TC%\tests" robocopy "%SRC_TC%\tests" "%DST_TC%\tests" /E /NFL /NDL /NJH /NJS /nc /ns /np >nul
if exist "%SRC_TC%\docs" robocopy "%SRC_TC%\docs" "%DST_TC%\docs" /E /NFL /NDL /NJH /NJS /nc /ns /np >nul

echo [+] Syncing TrueMkeyCollider runtime...
copy /Y "%SRC_MK%\TrueMkeyCollider.exe" "%DST_MK%\" >nul
if exist "%SRC_MK%\README.md" copy /Y "%SRC_MK%\README.md" "%DST_MK%\" >nul
if exist "%SRC_MK%\LICENSE" copy /Y "%SRC_MK%\LICENSE" "%DST_MK%\" >nul
if exist "%SRC_MK%\data" robocopy "%SRC_MK%\data" "%DST_MK%\data" /E /NFL /NDL /NJH /NJS /nc /ns /np >nul
if exist "%SRC_MK%\docs" robocopy "%SRC_MK%\docs" "%DST_MK%\docs" /E /NFL /NDL /NJH /NJS /nc /ns /np >nul

echo [+] Updating presets\user_settings.json ...
python -c "import json; from pathlib import Path; root=Path(r'%~dp0').resolve(); tc=root/'tools'/'TrueCollider'; mk=root/'tools'/'TrueMkeyCollider'; p=root/'presets'; p.mkdir(exist_ok=True); f=p/'user_settings.json'; cfg=json.loads(f.read_text(encoding='utf-8')) if f.exists() else {}; cfg.update({'truecollider_exe': str(tc/'keyhunt.exe'), 'truecollider_cuda': str(tc/'keyhunt_cuda.exe'), 'truemkey_exe': str(mk/'TrueMkeyCollider.exe'), 'workdir': str(tc), 'auto_configured': True}); f.write_text(json.dumps(cfg, indent=2), encoding='utf-8'); print('settings ok')"

echo.
echo Done. Bundled under:
echo   %DST_TC%
echo   %DST_MK%
pause

