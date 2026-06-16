@echo off
title Consolidador de Inadimplencias - MAT-INE 2026

echo.
echo  =========================================
echo   Consolidador de Inadimplencias - WEB
echo   Matricula EaD / Ineprotec
echo  =========================================
echo.
echo  Iniciando o servidor... aguarde alguns segundos.
echo.

start "" /B "C:\Users\Cliente\AppData\Local\Python\pythoncore-3.14-64\python.exe" "E:\PROJETOS IA\DEP-FINANCEIRO\DEP_FIN_COBRANCA\06_APP\app.py"

timeout /t 3 /nobreak > nul

start "" "http://localhost:5000"

echo  Servidor rodando em http://localhost:5000
echo  Feche esta janela quando terminar de usar.
echo.
pause
