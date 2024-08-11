# Define the default path to the Ollama executable
param (
    [string]$OllamaPath = "C:\Users\ZRD-AdminPBO\AppData\Local\Programs\Ollama\ollama.exe"
)

# Check if the Ollama executable exists
if (-Not (Test-Path $OllamaPath)) {
    Write-Host "The Ollama executable was not found at '$OllamaPath'." -ForegroundColor Red
    exit 1
}

# Execute the Ollama serve command in the background
try {
    Write-Host "Starting Ollama server in the background"
    $process = Start-Process -FilePath $OllamaPath `
                             -ArgumentList "serve" `
                             -PassThru `
                             -WindowStyle Hidden
    Write-Host "Ollama server started with PID $($process.Id)."

    # Wait briefly to ensure the server has time to start
    Start-Sleep -Seconds 2

    # Open the link in the default web browser
    $url = "http://localhost:11434/"
    Write-Host "Opening $url in the default web browser..."
    Start-Process $url
} catch {
    Write-Host "An error occurred while trying to start the Ollama server or open the URL: $_" -ForegroundColor Red
}
