# Define the Anaconda installation path, environment, and script details
$AnacondaPath = "$Env:ProgramData\Anaconda3"  # Path to Anaconda installation
$EnvName = "aider-ollama"  # Name of the Anaconda environment
$ScriptPath = "C:\projects\llama.cpp\projects\src\test.py"  # Path to the Python script

# Check if the script file exists
if (-Not (Test-Path $ScriptPath)) {
    Write-Host "The script '$ScriptPath' does not exist." -ForegroundColor Red
    exit 1
}

# Activate the Anaconda environment and run the script in a new window
try {
    Write-Host "Activating the Anaconda environment '$EnvName' and running the Python script '$ScriptPath' in a new window"

    # Command to activate the environment and run the script
    $command = "@echo off && call `"$AnacondaPath\Scripts\activate.bat`" $EnvName && python `"$ScriptPath`" && pause && conda deactivate"

    # Start a new Command Prompt window and execute the command
    Start-Process -FilePath "cmd.exe" -ArgumentList "/c", $command -WindowStyle Normal
} catch {
    Write-Host "An error occurred while trying to run the script: $_" -ForegroundColor Red
}
