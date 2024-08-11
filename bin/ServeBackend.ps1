# Function to load variables from a .env.local file
function Load-EnvFile($envFilePath) {
    if (-Not (Test-Path $envFilePath)) {
        Write-Host "The .env.local file '$envFilePath' does not exist." -ForegroundColor Red
        exit 1
    }

    $envContent = Get-Content $envFilePath | Where-Object { $_ -match "=" }
    $envContent | ForEach-Object {
        $key, $value = $_ -split '=', 2
        Set-Item -Path "Env:$key" -Value ($value -replace '"', '').Trim()
    }
}

# Load environment variables from .env.local file located one directory up
$envFilePath = "..\.env.local"
Load-EnvFile $envFilePath

# Define the Anaconda environment and script details from .env.local
$EnvName = $Env:BackendEnvName
$ScriptPath = $Env:BackendScriptPath

# Check if the script file exists
if (-Not (Test-Path $ScriptPath)) {
    Write-Host "The script '$ScriptPath' does not exist." -ForegroundColor Red
    exit 1
}

# Activate the Anaconda environment and run the script in a new window
try {
    Write-Host "Activating the Anaconda environment '$EnvName' and running the Python script '$ScriptPath' in a new window"

    # Command to activate the environment and run the script
    $command = "@echo off && call `"%ProgramData%\Anaconda3\Scripts\activate.bat`" $EnvName && python `"$ScriptPath`" && pause && conda deactivate"

    # Start a new Command Prompt window and execute the command
    Start-Process -FilePath "cmd.exe" -ArgumentList "/c", $command -WindowStyle Normal
} catch {
    Write-Host "An error occurred while trying to run the script: $_" -ForegroundColor Red
}
