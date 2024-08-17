# Hudini - CPU Magician on SLM

![Hudini Logo](./src/assets/hidini2.webp)

**CAUTION: FOR TESTING PURPOSES ONLY. NOT FOR PRODUCTION USE.**

Hudini is an interactive chat interface that works with CPU magic on SLM, allowing real-time prompt input and response generation.

## Features

- Interactive chat interface with real-time responses
- Previous prompts management (save, load, delete)
- Responsive UI design
- API documentation with Swagger
- Interactive API exploration with Swagger UI

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
   The `requirements.txt` file is located at `projects/src/llama-cpp-chat/src/backend/requirements.txt`. To install the required Python packages, navigate to this directory and run:
   ```bash
   cd projects/src/llama-cpp-chat/src/backend
   pip install -r requirements.txt
   ```
   This will install all the necessary Python dependencies for the project.

3. Configure `.env.local` in the project root:
   ```plaintext
   # Backend script configuration
    ANACONDA_ENV_NAME=<you name of anaconda env>
    #Urls
    SERVER_URL=http://localhost:5000
    #Models
    PROJECT_MODEL_PATH=C:\\projects\\llama.cpp\\models\\custom\
    # directories
    PROJEKT_ROOT=C:\projects\llama.cpp\projects\src\llama-cpp-chat\src
    #API Keys
    API_KEY_OPEN_AI=<apikey>
   ```

4. Install the Llama Model:
   ```bash
   huggingface-cli login
   huggingface-cli download TheBloke/LLaMA-7b-GGUF llama-7b.Q4_K_M.gguf --local-dir C:/projects/llama-cpp/models/custom --local-dir-use-symlinks False
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
   cd llama-cpp-chat/src/backend
   python server.py
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
- Swagger YAML: [http://localhost:5000/swagger.yaml](http://localhost:5000/swagger.yaml)
- Swagger UI: [http://localhost:5000/api/docs](http://localhost:5000/api/docs)

## Directory Structure

```
llama-cpp-chat/
├── bin/
│   └── (PowerShell scripts)
├── src/
│   ├── backend/
│   │   ├── clients/
│   │   ├── tests/
│   │   ├── requirements.txt
│   │   └── server.py
│   ├── assets/
│   └── components/
├── .env.local
└── README.md
```

## Running Tests

The test suite for Hudini is located in the `llama-cpp-chat/src/backend/tests` directory. These tests ensure that all API endpoints are functioning correctly. To run the tests, follow these steps:

1. Ensure your virtual environment is activated (if you're using one).

2. Make sure the backend server is running. If it's not, start it in a separate terminal:
   ```bash
   cd llama-cpp-chat/src/backend
   python server.py
   ```

3. Navigate to the test directory:
   ```bash
   cd llama-cpp-chat/src/backend/tests
   ```

4. Run all tests:
   ```bash
   python -m unittest test_api.py
   ```

### Running Specific Tests

You can run specific test methods using the following format:

```bash
python -m unittest test_api.TestLlamaCppChatAPI.<test_method_name>
```

Available test methods include:

- `test_get_models`: Tests the `/get_models` endpoint
- `test_generate`: Tests the `/generate` endpoint
- `test_stream`: Tests the `/stream` endpoint
- `test_load_prompts`: Tests the `/load_prompts` endpoint
- `test_save_and_delete_prompt`: Tests the `/save_prompt` and `/delete_prompt` endpoints
- `test_swagger_yaml`: Tests the `/swagger.yaml` endpoint

For example, to run only the test for the Swagger YAML endpoint:

```bash
python -m unittest test_api.TestLlamaCppChatAPI.test_swagger_yaml
```

### Understanding Test Results

When you run the tests, you'll see output indicating which tests passed or failed. A successful test run will look something like this:

```
......
----------------------------------------------------------------------
Ran 6 tests in X.XXXs

OK
```

If a test fails, you'll see more detailed output indicating which test failed and why. For example:

```
F.....
======================================================================
FAIL: test_swagger_yaml (test_api.TestLlamaCppChatAPI)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "test_api.py", line XX, in test_swagger_yaml
    self.assertEqual(response.status_code, 200)
AssertionError: 500 != 200

----------------------------------------------------------------------
Ran 6 tests in X.XXXs

FAILED (failures=1)
```

In this case, the test_swagger_yaml test failed because it received a 500 status code instead of the expected 200. This information can help you identify and fix issues in your API.

## API Endpoints

- GET `/load_prompts`: Retrieve previous prompts
- POST `/generate`: Send a prompt for response
- POST `/save_prompt`: Save a new prompt
- DELETE `/delete_prompt/:id`: Remove a prompt
- GET `/swagger.yaml`: Retrieve Swagger API documentation
- GET `/api/docs`: Access Swagger UI for interactive API exploration

## API Documentation

The API documentation is available in two formats:

1. Swagger/OpenAPI YAML: You can access the raw YAML file by visiting [http://localhost:5000/swagger.yaml](http://localhost:5000/swagger.yaml) when the backend server is running. This YAML file can be used with Swagger UI or other OpenAPI-compatible tools to explore and interact with the API.

2. Swagger UI: For an interactive documentation experience, visit [http://localhost:5000/api/docs](http://localhost:5000/api/docs). This interface allows you to explore the API endpoints, see request/response examples, and even try out the API directly from your browser.

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
