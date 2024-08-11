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

# Define the directory where the npm script should be run from .env.local
$DirectoryPath = $Env:FrontendDirectoryPath

# Check if the directory exists
if (-Not (Test-Path $DirectoryPath)) {
    Write-Host "The directory '$DirectoryPath' does not exist." -ForegroundColor Red
    exit 1
}

# Command to change to the project directory and run 'npm run dev'
$command = "cd `"$DirectoryPath`" && npm run dev"

# Start a new Command Prompt window and execute the command
try {
    Write-Host "Running 'npm run dev' in directory '$DirectoryPath' in a new window"
    Start-Process -FilePath "cmd.exe" -ArgumentList "/c", $command -WindowStyle Normal
} catch {
    Write-Host "An error occurred while trying to run 'npm run dev': $_" -ForegroundColor Red
}
