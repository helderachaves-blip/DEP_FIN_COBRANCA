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

start "" /B "C:\Users\Lorena\AppData\Local\Programs\Python\Python314\python.exe" "F:\DADOS\CONSULTORIA\EDILVO SOUSA\AUTOMACOES IA\DEP-FINANCEIRO\MAT-INE - INADIMPLENCIA - 2026\06_APP\app.py"

timeout /t 3 /nobreak > nul

start "" "http://localhost:5000"

echo  Servidor rodando em http://localhost:5000
echo  Feche esta janela quando terminar de usar.
echo.
pause
