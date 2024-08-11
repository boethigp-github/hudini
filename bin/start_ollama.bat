@echo off
:: Define the path to the Ollama executable with the serve argument
set "ollamaPath=C:\Users\ZRD-AdminPBO\AppData\Local\Programs\Ollama\ollama.exe serve"

:: Run the Ollama application in the background
start "" %ollamaPath%

:: Message indicating the application has been started
echo Ollama has been started and is running in the background.

:: Pause to keep the window open after execution
pause