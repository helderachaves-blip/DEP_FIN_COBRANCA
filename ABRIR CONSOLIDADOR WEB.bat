@echo off
title Consolidador de Inadimplencias - MAT-INE 2026

echo.
echo  =========================================
echo   Consolidador de Inadimplencias - WEB
echo   Matricula EaD / Ineprotec
echo  =========================================
echo.

REM Caminhos dinamicos: este .bat fica na raiz do projeto; o app esta em 06_APP.
REM %~dp0 = pasta deste .bat (com barra final) -> funciona em qualquer maquina/drive.
set "BASEDIR=%~dp0"
set "APPDIR=%BASEDIR%06_APP"

if not exist "%APPDIR%\app.py" (
  echo  [ERRO] Nao encontrei "%APPDIR%\app.py".
  echo  Mantenha este .bat na raiz do projeto, ao lado da pasta 06_APP.
  echo.
  pause
  exit /b 1
)

REM Detecta o Python: prefere o launcher 'py', cai para 'python' na PATH.
set "PYEXE="
where py >nul 2>&1 && set "PYEXE=py"
if not defined PYEXE ( where python >nul 2>&1 && set "PYEXE=python" )
if not defined PYEXE (
  echo  [ERRO] Python nao encontrado na PATH.
  echo  Instale o Python 3.10+ e marque "Add to PATH" no instalador.
  echo.
  pause
  exit /b 1
)

echo  Iniciando o servidor com: %PYEXE%
echo  Aguarde alguns segundos...
echo.

cd /d "%APPDIR%"
start "Consolidador (servidor)" /B %PYEXE% "%APPDIR%\app.py"

timeout /t 3 /nobreak >nul

start "" "http://localhost:5000"

echo  Servidor rodando em http://localhost:5000
echo  Feche esta janela quando terminar de usar.
echo.
pause
