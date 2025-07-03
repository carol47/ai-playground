@echo off
setlocal EnableDelayedExpansion

:: Kill All Node, Python, and LLM Processes - Batch Version
:: Created for Transcription Outpost - Debug Helper
:: Logs all actions and results

set LOGFILE=kill-processes-log.txt
set TIMESTAMP=%date% %time%

echo ============================================================ > %LOGFILE%
echo [%TIMESTAMP%] TRANSCRIPTION OUTPOST - PROCESS KILLER STARTED >> %LOGFILE%
echo ============================================================ >> %LOGFILE%
echo.
echo [%TIMESTAMP%] TRANSCRIPTION OUTPOST - PROCESS KILLER STARTED
echo ============================================================

:: Function to log with timestamp
call :LogMessage "SCANNING FOR PROCESSES"
echo ============================================================ >> %LOGFILE%

:: Check what processes are running before killing
echo Checking for Node processes...
call :LogMessage "Checking for Node processes..."
tasklist /FI "IMAGENAME eq node.exe" 2>&1 | findstr /C:"node.exe" >> %LOGFILE%
if %ERRORLEVEL% EQU 0 (
    tasklist /FI "IMAGENAME eq node.exe" | findstr /C:"node.exe"
    call :LogMessage "Found Node processes running"
) else (
    call :LogMessage "No Node processes found"
)

echo.
echo Checking for Python processes...
call :LogMessage "Checking for Python processes..."
tasklist /FI "IMAGENAME eq python.exe" 2>&1 | findstr /C:"python.exe" >> %LOGFILE%
if %ERRORLEVEL% EQU 0 (
    tasklist /FI "IMAGENAME eq python.exe" | findstr /C:"python.exe"
    call :LogMessage "Found Python processes running"
) else (
    call :LogMessage "No Python processes found"
)

echo.
echo Checking for Ollama processes...
call :LogMessage "Checking for Ollama processes..."
tasklist /FI "IMAGENAME eq ollama app.exe" 2>&1 | findstr /C:"ollama app.exe" >> %LOGFILE%
if %ERRORLEVEL% EQU 0 (
    tasklist /FI "IMAGENAME eq ollama app.exe" | findstr /C:"ollama app.exe"
    call :LogMessage "Found Ollama App processes running"
) else (
    call :LogMessage "No Ollama App processes found"
)
tasklist /FI "IMAGENAME eq ollama.exe" 2>&1 | findstr /C:"ollama.exe" >> %LOGFILE%
if %ERRORLEVEL% EQU 0 (
    tasklist /FI "IMAGENAME eq ollama.exe" | findstr /C:"ollama.exe"
    call :LogMessage "Found Ollama Server processes running"
) else (
    call :LogMessage "No Ollama Server processes found"
)

echo.
echo Checking for other LLM processes...
call :LogMessage "Checking for other LLM processes..."
set LLM_PROCESSES=lmstudio.exe gpt4all.exe koboldcpp.exe textgen.exe llamacpp.exe
for %%p in (%LLM_PROCESSES%) do (
    tasklist /FI "IMAGENAME eq %%p" 2>&1 | findstr /C:"%%p" >> %LOGFILE%
    if !ERRORLEVEL! EQU 0 (
        tasklist /FI "IMAGENAME eq %%p" | findstr /C:"%%p"
        call :LogMessage "Found %%p running"
    )
)

:: Check port usage
echo.
call :LogMessage "CHECKING PORT USAGE"
echo ============================================================ >> %LOGFILE%

set PORTS=3001 8000 3000 3002 11434 8080 5000 7860 5001
for %%p in (%PORTS%) do (
    echo Checking port %%p...
    call :LogMessage "Checking port %%p..."
    netstat -an | findstr ":%%p " > nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        call :LogMessage "Port %%p is in use:"
        netstat -an | findstr ":%%p " >> %LOGFILE%
        netstat -an | findstr ":%%p "
    ) else (
        call :LogMessage "Port %%p is free"
    )
)

:: Start killing processes
echo.
call :LogMessage "TERMINATING PROCESSES"
echo ============================================================ >> %LOGFILE%

set /a TOTAL_KILLED=0
set /a FAILED_KILLS=0

:: Kill Node processes
echo.
echo Killing Node processes...
call :LogMessage "Attempting to kill Node processes..."
taskkill /F /IM node.exe > nul 2>&1
if %ERRORLEVEL% EQU 0 (
    call :LogMessage "✓ Successfully killed Node processes"
    echo ✓ Successfully killed Node processes
    set /a TOTAL_KILLED+=1
) else (
    call :LogMessage "✗ No Node processes to kill or kill failed"
    echo ✗ No Node processes to kill or kill failed
)

:: Kill Python processes
echo.
echo Killing Python processes...
call :LogMessage "Attempting to kill Python processes..."
taskkill /F /IM python.exe > nul 2>&1
if %ERRORLEVEL% EQU 0 (
    call :LogMessage "✓ Successfully killed Python processes"
    echo ✓ Successfully killed Python processes
    set /a TOTAL_KILLED+=1
) else (
    call :LogMessage "✗ No Python processes to kill or kill failed"
    echo ✗ No Python processes to kill or kill failed
)

:: Kill Ollama processes
echo.
echo Killing Ollama processes...
call :LogMessage "Attempting to kill Ollama processes..."
taskkill /F /IM "ollama app.exe" > nul 2>&1
if %ERRORLEVEL% EQU 0 (
    call :LogMessage "✓ Successfully killed Ollama App processes"
    echo ✓ Successfully killed Ollama App processes
    set /a TOTAL_KILLED+=1
) else (
    call :LogMessage "✗ No Ollama App processes to kill or kill failed"
    echo ✗ No Ollama App processes to kill or kill failed
)
taskkill /F /IM ollama.exe > nul 2>&1
if %ERRORLEVEL% EQU 0 (
    call :LogMessage "✓ Successfully killed Ollama Server processes"
    echo ✓ Successfully killed Ollama Server processes
    set /a TOTAL_KILLED+=1
) else (
    call :LogMessage "✗ No Ollama Server processes to kill or kill failed"
    echo ✗ No Ollama Server processes to kill or kill failed
)

:: Kill other LLM processes
echo.
echo Killing other LLM processes...
call :LogMessage "Attempting to kill other LLM processes..."
for %%p in (%LLM_PROCESSES%) do (
    taskkill /F /IM %%p > nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        call :LogMessage "✓ Successfully killed %%p"
        echo ✓ Successfully killed %%p
        set /a TOTAL_KILLED+=1
    )
)

:: Wait for processes to terminate
echo.
call :LogMessage "Waiting 3 seconds for processes to fully terminate..."
echo Waiting 3 seconds for processes to fully terminate...
timeout /t 3 /nobreak > nul

:: Verify cleanup
echo.
call :LogMessage "VERIFICATION - CHECKING REMAINING PROCESSES"
echo ============================================================ >> %LOGFILE%

echo Verifying Node processes are gone...
call :LogMessage "Verifying Node processes are gone..."
tasklist /FI "IMAGENAME eq node.exe" 2>&1 | findstr /C:"node.exe" > nul
if %ERRORLEVEL% EQU 0 (
    call :LogMessage "⚠ WARNING: Node processes still running!"
    echo ⚠ WARNING: Node processes still running!
    tasklist /FI "IMAGENAME eq node.exe" | findstr /C:"node.exe"
    tasklist /FI "IMAGENAME eq node.exe" | findstr /C:"node.exe" >> %LOGFILE%
) else (
    call :LogMessage "✓ All Node processes successfully terminated"
    echo ✓ All Node processes successfully terminated
)

echo.
echo Verifying Python processes are gone...
call :LogMessage "Verifying Python processes are gone..."
tasklist /FI "IMAGENAME eq python.exe" 2>&1 | findstr /C:"python.exe" > nul
if %ERRORLEVEL% EQU 0 (
    call :LogMessage "⚠ WARNING: Python processes still running!"
    echo ⚠ WARNING: Python processes still running!
    tasklist /FI "IMAGENAME eq python.exe" | findstr /C:"python.exe"
    tasklist /FI "IMAGENAME eq python.exe" | findstr /C:"python.exe" >> %LOGFILE%
) else (
    call :LogMessage "✓ All Python processes successfully terminated"
    echo ✓ All Python processes successfully terminated
)

echo.
echo Verifying Ollama processes are gone...
call :LogMessage "Verifying Ollama processes are gone..."
tasklist /FI "IMAGENAME eq ollama app.exe" 2>&1 | findstr /C:"ollama app.exe" > nul
if %ERRORLEVEL% EQU 0 (
    call :LogMessage "⚠ WARNING: Ollama App processes still running!"
    echo ⚠ WARNING: Ollama App processes still running!
    tasklist /FI "IMAGENAME eq ollama app.exe" | findstr /C:"ollama app.exe"
    tasklist /FI "IMAGENAME eq ollama app.exe" | findstr /C:"ollama app.exe" >> %LOGFILE%
) else (
    call :LogMessage "✓ All Ollama App processes successfully terminated"
    echo ✓ All Ollama App processes successfully terminated
)
tasklist /FI "IMAGENAME eq ollama.exe" 2>&1 | findstr /C:"ollama.exe" > nul
if %ERRORLEVEL% EQU 0 (
    call :LogMessage "⚠ WARNING: Ollama Server processes still running!"
    echo ⚠ WARNING: Ollama Server processes still running!
    tasklist /FI "IMAGENAME eq ollama.exe" | findstr /C:"ollama.exe"
    tasklist /FI "IMAGENAME eq ollama.exe" | findstr /C:"ollama.exe" >> %LOGFILE%
) else (
    call :LogMessage "✓ All Ollama Server processes successfully terminated"
    echo ✓ All Ollama Server processes successfully terminated
)

:: Final port check
echo.
call :LogMessage "FINAL PORT STATUS CHECK"
echo ============================================================ >> %LOGFILE%

for %%p in (%PORTS%) do (
    echo Checking port %%p...
    call :LogMessage "Final check - Port %%p..."
    netstat -an | findstr ":%%p " > nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        call :LogMessage "⚠ Port %%p still in use:"
        echo ⚠ Port %%p still in use:
        netstat -an | findstr ":%%p " >> %LOGFILE%
        netstat -an | findstr ":%%p "
    ) else (
        call :LogMessage "✓ Port %%p is now free"
        echo ✓ Port %%p is now free
    )
)

:: Summary
echo.
call :LogMessage "EXECUTION SUMMARY"
echo ============================================================ >> %LOGFILE%
call :LogMessage "Script completed successfully!"
echo ✓ Script completed successfully!

set TIMESTAMP=%date% %time%
echo ============================================================ >> %LOGFILE%
echo [%TIMESTAMP%] TRANSCRIPTION OUTPOST - PROCESS KILLER COMPLETED >> %LOGFILE%
echo ============================================================ >> %LOGFILE%
echo.
echo ============================================================
echo [%TIMESTAMP%] TRANSCRIPTION OUTPOST - PROCESS KILLER COMPLETED
echo ============================================================
echo.
echo Log file saved to: %LOGFILE%
echo.
pause
goto :eof

:: Function to log messages with timestamp
:LogMessage
set TIMESTAMP=%date% %time%
echo [%TIMESTAMP%] %~1
echo [%TIMESTAMP%] %~1 >> %LOGFILE%
goto :eof 