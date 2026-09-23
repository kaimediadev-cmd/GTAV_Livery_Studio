@echo off
chcp 65001 >nul
title Build GTAV Livery Studio (Single File Standalone)
echo =======================================================
echo  DANG XUAT BAN (PUBLISH) 1 FILE EXE DUY NHAT (.NET 8)...
echo  (Nhung ngam CodeWalker, SharpDX va Python Script)
echo =======================================================
echo.

:: Tat app neu dang chay ngam de khong bi khoa file
taskkill /f /im GTAV_Livery_Studio.exe >nul 2>&1

:: Don dep cac file cu neu co trong thu muc dich
if exist "..\GTAV_Livery_Studio\Auto_Export_UV_Template.py" del /f /q "..\GTAV_Livery_Studio\Auto_Export_UV_Template.py"
del /f /q "..\GTAV_Livery_Studio\*.dll" >nul 2>&1
del /f /q "..\GTAV_Livery_Studio\*.pdb" >nul 2>&1
del /f /q "..\GTAV_Livery_Studio\*.json" >nul 2>&1
del /f /q "..\GTAV_Livery_Studio\*.ico" >nul 2>&1
del /f /q "..\GTAV_Livery_Studio\*.png" >nul 2>&1

dotnet publish GTAV_Livery_Studio.csproj -c Release -o "..\GTAV_Livery_Studio"
if %ERRORLEVEL% NEQ 0 goto :failed

if exist "..\GTAV_Livery_Studio\GTAV_Livery_Studio.pdb" del /f /q "..\GTAV_Livery_Studio\GTAV_Livery_Studio.pdb"
echo.
echo =======================================================
echo  XUAT BAN THANH CONG! CHI CON 1 FILE .EXE DUY NHAT TAI:
echo  ..\GTAV_Livery_Studio\GTAV_Livery_Studio.exe
echo  [Ma nguon .py da duoc nhung ngam ben trong .exe]
echo =======================================================
goto :done

:failed
echo.
echo =======================================================
echo  BUILD THAT BAI! Vui long kiem tra thong bao loi ben tren.
echo =======================================================

:done
echo.
pause