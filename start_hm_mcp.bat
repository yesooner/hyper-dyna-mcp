@echo off
set "ALTAIR_HOME=E:\HM2021\2021\hwdesktop"
set "PATH=%ALTAIR_HOME%\hm\bin\win64;%ALTAIR_HOME%\hw\bin\win64;%PATH%"
set "TCL_LIBRARY=%ALTAIR_HOME%\hw\tcl\tcl8.5.9\win64\lib\tcl8.5"

echo Starting HyperWorks with Dyna-mcp listener...
echo Listener will auto-load on port 47881
echo.

start "" "%ALTAIR_HOME%\hw\bin\win64\hw.exe" -tcl "source \"F:/Dyna-mcp/runs/mcp.tcl\""

echo HyperWorks launched. Listener ready in ~10 seconds.
