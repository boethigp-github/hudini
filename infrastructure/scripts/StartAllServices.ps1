# Define script names assuming all scripts are in the same directory as the master script
$BackendScript = ".\ServeBackend.ps1"
$FrontendDevScript = ".\ServeFrontendDev.ps1"
$OllamaScript = ".\ServeOlllama.ps1"

# Function to run a script in a new Command Prompt window and close the window
function Run-ScriptAndClose($scriptPath) {
    if (-Not (Test-Path $scriptPath)) {
        Write-Host "The script '$scriptPath' does not exist." -ForegroundColor Red
        return
    }

    try {
        Write-Host "Running script '$scriptPath' in a new window"
        # Use Start-Process to open a new cmd.exe window, run the script, and close it
        Start-Process -FilePath "cmd.exe" -ArgumentList "/c", "powershell.exe -ExecutionPolicy Bypass -File `"$scriptPath`"" -WindowStyle Hidden
    } catch {
        Write-Host "An error occurred while trying to run the script '$scriptPath': $_" -ForegroundColor Red
    }
}

# Run each script
Run-ScriptAndClose $BackendScript
Run-ScriptAndClose $FrontendDevScript
Run-ScriptAndClose $OllamaScript
# Return to the original location

