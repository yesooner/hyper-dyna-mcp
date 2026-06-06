@echo off
REM LS-DYNA environment setup for ANSYS 2022R2
REM Run this before executing LS-DYNA solver

set ANSYS_SYSDIR=winx64
set ANSYS_DIR=E:\ANSYS2022\ANSYS Inc\v222\ansys
set AWP_ROOT222=E:\ANSYS2022\ANSYS Inc\v222
set ANSYSLMD_LICENSE_FILE=1055@localhost

echo LS-DYNA environment configured:
echo   ANSYS_SYSDIR=%ANSYS_SYSDIR%
echo   ANSYS_DIR=%ANSYS_DIR%
echo   AWP_ROOT222=%AWP_ROOT222%
echo   ANSYSLMD_LICENSE_FILE=%ANSYSLMD_LICENSE_FILE%
