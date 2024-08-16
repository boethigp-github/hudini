# Hudini - CPU Magician on SLM

![Hudini Logo](./src/assets/hidini2.webp)

**CAUTION: FOR TESTING PURPOSES ONLY. NOT FOR PRODUCTION USE.**

Hudini is an interactive chat interface that works with CPU magic on SLM, allowing real-time prompt input and response generation.

## Features

- Interactive chat interface with real-time responses
- Previous prompts management (save, load, delete)
- Responsive UI design

## Prerequisites

- [Node.js](https://nodejs.org/) (v12+)
- [Git](https://git-scm.com/)
- [Python](https://www.python.org/) (3.7+)

## Setup

1. Clone the repository and install dependencies:
   ```bash
   git clone <repository-url>
   cd hudini
   npm install
   ```

2. Install required Python packages:
   ```bash
   pip install openai flask flask-cors python-dotenv huggingface-hub
   ```

3. Configure `.env.local` in the project root:
   ```plaintext
   BackendScriptPath=C:\projects\llama.cpp\projects\src\llama-cpp-chat\src\backend\server.py
   FrontendDirectoryPath=C:\projects\llama.cpp\projects\src\llama-cpp-chat
   OllamaPath=<your userdir>AppData\Local\Programs\Olalama\ollama.exe
   API_KEY_OPEN_AI=<Your Open API Key>
   SERVER_URL=http://localhost:5000
   ```

4. Install the Llama Model:
   ```bash
   huggingface-cli login
   huggingface-cli download TheBloke/LLaMA-7b-GGUF llama-7b.Q4_K_M.gguf --local-dir C:/projects/llama-cpp --local-dir-use-symlinks False
   ```

## Running the Application

### Automated Start (All Services)

```powershell
cd <project_root>/bin
.\StartAllServices.ps1
```

### Manual Start

1. Backend Server:
   ```bash
   cd <project_root>/src
  python -m backend.server
   ```

2. Frontend Development Server:
   ```bash
   cd <project_root>
   npm run dev
   ```

3. Ollama Server:
   ```bash
   <your userdir>\AppData\Local\Programs\Ollama\ollama.exe serve
   ```

## Access Points

- Frontend: [http://localhost:5173](http://localhost:5173)
- Backend API: [http://localhost:5000](http://localhost:5000)
- Ollama server: [http://localhost:11434](http://localhost:11434)

## Directory Structure

```
llama-cpp-chat/
├── bin/
│   └── (PowerShell scripts)
├── src/
│   ├── backend/
│   │   ├── clients/
│   │   ├── tests/
│   │   └── server.py
│   ├── assets/
│   └── components/
├── .env.local
└── README.md
```

## Running Tests

```bash
cd <project_root>/src/backend/tests
python test_api.py
```

## API Endpoints

- GET `/load_prompts`: Retrieve previous prompts
- POST `/generate`: Send a prompt for response
- POST `/save_prompt`: Save a new prompt
- DELETE `/delete_prompt/:id`: Remove a prompt

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit changes
4. Push to the branch
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Contact

For inquiries, contact [Your Name] at [your.email@example.com].


