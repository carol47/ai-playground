# Kill All Node and Python Processes Script
# Created for Transcription Outpost - Debug Helper
# Logs all actions and results

param(
    [string]$LogFile = "kill-processes-log.txt"
)

# Function to write timestamped log entries
function Write-LogEntry {
    param([string]$Message, [string]$Type = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] [$Type] $Message"
    Write-Host $LogEntry
    $LogEntry | Out-File -FilePath $LogFile -Append -Encoding UTF8
}

# Function to log separator
function Write-LogSeparator {
    param([string]$Title)
    $Separator = "=" * 60
    Write-LogEntry $Separator
    Write-LogEntry $Title
    Write-LogEntry $Separator
}

# Start logging
Write-LogSeparator "TRANSCRIPTION OUTPOST - PROCESS KILLER STARTED"

try {
    # Show current processes before killing
    Write-LogSeparator "SCANNING FOR PROCESSES"
    
    # Get all Node processes
    $NodeProcesses = Get-Process -Name "*node*" -ErrorAction SilentlyContinue
    if ($NodeProcesses) {
        Write-LogEntry "Found $($NodeProcesses.Count) Node processes:"
        foreach ($proc in $NodeProcesses) {
            Write-LogEntry "  - PID: $($proc.Id), Name: $($proc.ProcessName), CPU: $($proc.CPU)"
        }
    } else {
        Write-LogEntry "No Node processes found" "INFO"
    }
    
    # Get all Python processes
    $PythonProcesses = Get-Process -Name "*python*" -ErrorAction SilentlyContinue
    if ($PythonProcesses) {
        Write-LogEntry "Found $($PythonProcesses.Count) Python processes:"
        foreach ($proc in $PythonProcesses) {
            Write-LogEntry "  - PID: $($proc.Id), Name: $($proc.ProcessName), CPU: $($proc.CPU)"
        }
    } else {
        Write-LogEntry "No Python processes found" "INFO"
    }
    
    # Get all Uvicorn processes
    $UvicornProcesses = Get-Process -Name "*uvicorn*" -ErrorAction SilentlyContinue
    if ($UvicornProcesses) {
        Write-LogEntry "Found $($UvicornProcesses.Count) Uvicorn processes:"
        foreach ($proc in $UvicornProcesses) {
            Write-LogEntry "  - PID: $($proc.Id), Name: $($proc.ProcessName), CPU: $($proc.CPU)"
        }
    } else {
        Write-LogEntry "No Uvicorn processes found" "INFO"
    }
    
    # Check port usage
    Write-LogSeparator "CHECKING PORT USAGE"
    $PortsToCheck = @(3001, 8000, 3000, 3002)
    foreach ($port in $PortsToCheck) {
        $PortUsage = netstat -ano | findstr ":$port "
        if ($PortUsage) {
            Write-LogEntry "Port $port is in use:"
            foreach ($line in $PortUsage) {
                Write-LogEntry "  $line"
            }
        } else {
            Write-LogEntry "Port $port is free"
        }
    }
    
    # Start killing processes
    Write-LogSeparator "TERMINATING PROCESSES"
    
    $TotalKilled = 0
    $FailedKills = 0
    
    # Kill Node processes
    if ($NodeProcesses) {
        Write-LogEntry "Terminating $($NodeProcesses.Count) Node processes..."
        foreach ($proc in $NodeProcesses) {
            try {
                Stop-Process -Id $proc.Id -Force -ErrorAction Stop
                Write-LogEntry "✓ Killed Node process PID: $($proc.Id)" "SUCCESS"
                $TotalKilled++
            } catch {
                Write-LogEntry "✗ Failed to kill Node process PID: $($proc.Id) - $($_.Exception.Message)" "ERROR"
                $FailedKills++
            }
        }
    }
    
    # Kill Python processes
    if ($PythonProcesses) {
        Write-LogEntry "Terminating $($PythonProcesses.Count) Python processes..."
        foreach ($proc in $PythonProcesses) {
            try {
                Stop-Process -Id $proc.Id -Force -ErrorAction Stop
                Write-LogEntry "✓ Killed Python process PID: $($proc.Id)" "SUCCESS"
                $TotalKilled++
            } catch {
                Write-LogEntry "✗ Failed to kill Python process PID: $($proc.Id) - $($_.Exception.Message)" "ERROR"
                $FailedKills++
            }
        }
    }
    
    # Kill Uvicorn processes
    if ($UvicornProcesses) {
        Write-LogEntry "Terminating $($UvicornProcesses.Count) Uvicorn processes..."
        foreach ($proc in $UvicornProcesses) {
            try {
                Stop-Process -Id $proc.Id -Force -ErrorAction Stop
                Write-LogEntry "✓ Killed Uvicorn process PID: $($proc.Id)" "SUCCESS"
                $TotalKilled++
            } catch {
                Write-LogEntry "✗ Failed to kill Uvicorn process PID: $($proc.Id) - $($_.Exception.Message)" "ERROR"
                $FailedKills++
            }
        }
    }
    
    # Use taskkill as backup
    Write-LogSeparator "BACKUP CLEANUP WITH TASKKILL"
    
    try {
        $TaskkillNode = taskkill /F /IM node.exe 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-LogEntry "✓ taskkill successfully cleaned up node.exe processes" "SUCCESS"
        } else {
            Write-LogEntry "taskkill for node.exe: $TaskkillNode" "INFO"
        }
    } catch {
        Write-LogEntry "taskkill for node.exe failed: $($_.Exception.Message)" "WARN"
    }
    
    try {
        $TaskkillPython = taskkill /F /IM python.exe 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-LogEntry "✓ taskkill successfully cleaned up python.exe processes" "SUCCESS"
        } else {
            Write-LogEntry "taskkill for python.exe: $TaskkillPython" "INFO"
        }
    } catch {
        Write-LogEntry "taskkill for python.exe failed: $($_.Exception.Message)" "WARN"
    }
    
    # Wait a moment for processes to actually terminate
    Write-LogEntry "Waiting 3 seconds for processes to fully terminate..."
    Start-Sleep -Seconds 3
    
    # Verify cleanup
    Write-LogSeparator "VERIFICATION - CHECKING REMAINING PROCESSES"
    
    $RemainingNode = Get-Process -Name "*node*" -ErrorAction SilentlyContinue
    $RemainingPython = Get-Process -Name "*python*" -ErrorAction SilentlyContinue
    $RemainingUvicorn = Get-Process -Name "*uvicorn*" -ErrorAction SilentlyContinue
    
    if ($RemainingNode) {
        Write-LogEntry "⚠ WARNING: $($RemainingNode.Count) Node processes still running!" "WARN"
        foreach ($proc in $RemainingNode) {
            Write-LogEntry "  - PID: $($proc.Id), Name: $($proc.ProcessName)"
        }
    } else {
        Write-LogEntry "✓ All Node processes successfully terminated" "SUCCESS"
    }
    
    if ($RemainingPython) {
        Write-LogEntry "⚠ WARNING: $($RemainingPython.Count) Python processes still running!" "WARN"
        foreach ($proc in $RemainingPython) {
            Write-LogEntry "  - PID: $($proc.Id), Name: $($proc.ProcessName)"
        }
    } else {
        Write-LogEntry "✓ All Python processes successfully terminated" "SUCCESS"
    }
    
    if ($RemainingUvicorn) {
        Write-LogEntry "⚠ WARNING: $($RemainingUvicorn.Count) Uvicorn processes still running!" "WARN"
        foreach ($proc in $RemainingUvicorn) {
            Write-LogEntry "  - PID: $($proc.Id), Name: $($proc.ProcessName)"
        }
    } else {
        Write-LogEntry "✓ All Uvicorn processes successfully terminated" "SUCCESS"
    }
    
    # Final port check
    Write-LogSeparator "FINAL PORT STATUS CHECK"
    foreach ($port in $PortsToCheck) {
        $PortUsage = netstat -ano | findstr ":$port "
        if ($PortUsage) {
            Write-LogEntry "⚠ Port $port still in use:" "WARN"
            foreach ($line in $PortUsage) {
                Write-LogEntry "  $line"
            }
        } else {
            Write-LogEntry "✓ Port $port is now free" "SUCCESS"
        }
    }
    
    # Summary
    Write-LogSeparator "EXECUTION SUMMARY"
    Write-LogEntry "✓ Total processes killed: $TotalKilled" "SUCCESS"
    if ($FailedKills -gt 0) {
        Write-LogEntry "✗ Failed to kill: $FailedKills processes" "ERROR"
    }
    Write-LogEntry "Script completed successfully!"
    
} catch {
    Write-LogEntry "FATAL ERROR: $($_.Exception.Message)" "ERROR"
    Write-LogEntry "Stack trace: $($_.ScriptStackTrace)" "ERROR"
    exit 1
}

Write-LogSeparator "TRANSCRIPTION OUTPOST - PROCESS KILLER COMPLETED"
Write-LogEntry "Log file saved to: $LogFile" 