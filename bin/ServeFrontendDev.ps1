# Function to load variables from a .env.local file
function Load-EnvFile($envFilePath) {
    if (-Not $envFilePath) {
        Write-Host "The path to .env.local is not set." -ForegroundColor Red
        exit 1
    }

    if (-Not (Test-Path $envFilePath)) {
        Write-Host "The .env.local file '$envFilePath' does not exist." -ForegroundColor Red
        exit 1
    }

    $envContent = Get-Content $envFilePath | Where-Object { $_ -match "=" }
    $envContent | ForEach-Object {
        $key, $value = $_ -split '=', 2
        $trimmedKey = $key.Trim()
        $trimmedValue = $value.Trim().Trim('"')  # Trim spaces and surrounding quotes

        if ($trimmedKey) {
            Set-Item -Path "Env:$trimmedKey" -Value $trimmedValue
        } else {
            Write-Host "Skipping invalid entry in .env.local: $_" -ForegroundColor Yellow
        }
    }
}

# Set the path to .env.local (adjust as needed)
$envFilePath = "$PSScriptRoot\..\.env.local"

# Load environment variables
Load-EnvFile $envFilePath

# Define the directory where the npm script should be run
$DirectoryPath = $Env:PROJECT_FRONTEND_DIRECTORY

# Check if the directory path is valid
if (-Not $DirectoryPath) {
    Write-Host "The PROJECT_FRONTEND_DIRECTORY environment variable is not set." -ForegroundColor Red
    exit 1
}

if (-Not (Test-Path $DirectoryPath)) {
    Write-Host "The directory '$DirectoryPath' does not exist." -ForegroundColor Red
    exit 1
}

# Run 'npm run dev' in a new Command Prompt window
try {
    Write-Host "Running 'npm run dev' in directory '$DirectoryPath' in a new window"
    Start-Process -FilePath "cmd.exe" -ArgumentList "/c cd `"$DirectoryPath`" && npm run dev" -WindowStyle Normal
} catch {
    Write-Host "An error occurred while trying to run 'npm run dev': $_" -ForegroundColor Red
}
