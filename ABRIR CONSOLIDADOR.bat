@echo off
cd /d "%~dp0"

:: Tenta pythonw pelo PATH primeiro
where pythonw >nul 2>&1
if %errorlevel% equ 0 (
    pythonw "01_SCRIPTS\inadimplencia_app.py"
    goto :fim
)

:: Tenta localização padrão Python 3.14
set "PY314=%LOCALAPPDATA%\Programs\Python\Python314\pythonw.exe"
if exist "%PY314%" (
    "%PY314%" "01_SCRIPTS\inadimplencia_app.py"
    goto :fim
)

:: Tenta outras versões comuns
for %%V in (313 312 311 310 39) do (
    set "PYPATH=%LOCALAPPDATA%\Programs\Python\Python%%V\pythonw.exe"
    if exist "%PYPATH%" (
        "%PYPATH%" "01_SCRIPTS\inadimplencia_app.py"
        goto :fim
    )
)

:: Não encontrou
echo.
echo ERRO: Python nao foi encontrado no sistema.
echo.
echo Instale o Python em: https://www.python.org/downloads/
echo Marque a opcao "Add Python to PATH" durante a instalacao.
echo.
pause
exit /b 1

:fim
if %errorlevel% neq 0 (
    echo.
    echo ERRO ao abrir o app. Pressione qualquer tecla para ver o erro...
    pause > nul
)
