Here's the updated README with placeholders for API keys:

---

# Hudini - CPU Magician on SLM

![Hudini Logo](src/frontend/src/assets/hidini2.webp)

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
- [Anaconda](https://www.anaconda.com/) (for managing Python environments)

## Setup

1. **Clone the repository and install dependencies:**
   ```bash
   git clone <repository-url>
   cd llama-cpp-chat/frontend
   npm install
   ```

2. **Create the Anaconda environment:**
   You need to create an Anaconda environment with the name specified in the `.env.local` file. First, ensure that the `.env.local` file contains the environment name:

   **Example `.env.local` content:**
   ```plaintext
   ANACONDA_ENV_NAME=aider-ollama
   SERVER_URL=http://localhost:5000
   PROJECT_MODEL_PATH=C:\\projects\\llama.cpp\\models\\custom\
   PROJEKT_ROOT=C:\projects\llama.cpp\projects\src\llama-cpp-chat\src
   API_KEY_OPEN_AI=your-openai-api-key-here
   PROJECT_FRONTEND_DIRECTORY=C:\\projects\\llama.cpp\\projects\\src\\llama-cpp-chat\\src\\frontend\
   ```

   Then, create the Anaconda environment using the name from the `ANACONDA_ENV_NAME` variable:
   ```bash
   conda create --name aider-ollama python=3.8
   ```
   Activate the environment:
   ```bash
   conda activate aider-ollama
   ```

3. **Install required Python packages:**
   The `requirements.txt` file is located at `src/backend/requirements.txt`. To install the required Python packages, navigate to this directory and run:
   ```bash
   cd src/backend
   pip install -r requirements.txt
   ```
   This will install all the necessary Python dependencies for the project.

4. **Configure `.env.local` in the project root:**
   Ensure that your `.env.local` file is properly configured with all the necessary environment variables. Here is an example:
   ```plaintext
   ANACONDA_ENV_NAME=aider-ollama
   SERVER_URL=http://localhost:5000
   PROJECT_MODEL_PATH=C:\\projects\\llama.cpp\\models\\custom\
   PROJEKT_ROOT=C:\projects\llama.cpp\projects\src\llama-cpp-chat\src
   API_KEY_OPEN_AI=your-openai-api-key-here
   PROJECT_FRONTEND_DIRECTORY=C:\\projects\\llama.cpp\\projects\\src\\llama-cpp-chat\\src\\frontend\
   ```

5. **Install the Llama Model:**
   To download and install the Llama model, follow these steps:
   ```bash
   huggingface-cli login
   huggingface-cli download TheBloke/LLaMA-7b-GGUF llama-7b.Q4_K_M.gguf --local-dir C:/projects/llama-cpp/models/custom --local-dir-use-symlinks False
   ```

## Running the Application

### Automated Start (All Services)

To start all services (backend, frontend, and Ollama server) together, run the following PowerShell script:

```powershell
cd <project_root>/bin
.\StartAllServices.ps1
```

### Manual Start

If you prefer to start each service manually, follow these steps:

1. **Backend Server:**
   Navigate to the backend directory and start the server:
   ```bash
   cd src/backend
   python server.py
   ```

2. **Frontend Development Server:**
   Navigate to the frontend directory and start the development server:
   ```bash
   cd frontend
   npm run dev
   ```

3. **Ollama Server:**
   Start the Ollama server using the following command:
   ```bash
   <your userdir>\AppData\Local\Programs\Ollama\ollama.exe serve
   ```

## Access Points

- **Frontend:** [http://localhost:5173](http://localhost:5173)
- **Backend API:** [http://localhost:5000](http://localhost:5000)
- **Ollama server:** [http://localhost:11434](http://localhost:11434)
- **Swagger YAML:** [http://localhost:5000/swagger.yaml](http://localhost:5000/swagger.yaml)
- **Swagger UI:** [http://localhost:5000/api/docs](http://localhost:5000/api/docs)

## Directory Structure

```
llama-cpp-chat/
├── bin/
│   └── (PowerShell scripts for automated tasks)
├── src/
│   ├── backend/
│   │   ├── clients/
│   │   ├── tests/
│   │   ├── requirements.txt
│   │   ├── server.py
│   │   └── swagger.yaml
│   ├── frontend/
│   │   ├── node_modules/
│   │   ├── public/
│   │   ├── src/
│   │   │   ├── assets/
│   │   │   │   ├── chat-styles.css
│   │   │   │   ├── hidini2.webp
│   │   │   │   ├── hudini-logo.webp
│   │   │   │   └── vue.svg
│   │   │   ├── components/
│   │   │   │   ├── ChatForm.vue
│   │   │   │   ├── PromptPanel.vue
│   │   │   │   └── SseTestComponent.vue
│   │   │   ├── App.vue
│   │   │   ├── i18n.js
│   │   │   ├── index.html
│   │   │   └── main.js
│   │   ├── tests/
│   │   ├── package.json
│   │   ├── package-lock.json
│   │   ├── vite.config.js
│   │   └── vitest.setup.js
├── storage/
├── .env.local
├── .gitignore
└── README.md
```

## Running Tests

The test suite for Hudini is located in the `src/backend/tests` directory. These tests ensure that all API endpoints are functioning correctly. To run the tests, follow these steps:

1. **Activate your virtual environment** (if you're using one).

2. **Ensure the backend server is running.** If it's not, start it in a separate terminal:
   ```bash
   cd src/backend
   python server.py
   ```

3. **Navigate to the test directory:**
   ```bash
   cd src/backend/tests
   ```

4. **Run all tests:**
   ```bash
   python -m unittest discover
   ```

### Running Specific Tests

We are using `pytest`. You can run specific test methods using the following format:

```bash
pytest -v ./api # test complete API folder
pytest -v ./api/models/*
pytest -v ./api/models/test_models.py # specific file
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

In this case, the `test_swagger_yaml` test failed because it received a 500 status code instead of the expected 200. This information can help you identify and fix issues in your API.

## API Endpoints

- **GET** `/load_prompts`: Retrieve previous prompts
- **POST** `/generate`: Send a prompt for a response
- **POST** `/save_prompt`: Save a new prompt
- **DELETE** `/delete_prompt/:id`: Remove a prompt
- **GET** `/swagger.yaml`: Retrieve Swagger API documentation
- **GET** `/api/docs`: Access Swagger UI for interactive API exploration

## API Documentation

The API documentation is available in two formats:

1. **Swagger/OpenAPI YAML**: You can access the raw YAML file by visiting [http://localhost:5000/swagger.yaml](http://localhost:5000/swagger.yaml) when the backend server is running. This YAML file can be used with Swagger UI or other OpenAPI-compatible tools to explore and interact with the API.

2. **Swagger UI**: For an interactive documentation experience, visit [http://localhost:5000/api/docs

](http://localhost:5000/api/docs). This interface allows you to explore the API endpoints, see request/response examples, and even try out the API directly from your browser.

## Contributing

1. **Fork the repository**
2. **Create your feature branch**
3. **Commit changes**
4. **Push to the branch**
5. **Submit a pull request**

## License

This project is licensed under the MIT License.

## Contact

For inquiries, contact [Your Name] at [your.email@example.com].

---

This version of the README includes placeholders for API keys, ensuring sensitive information isn't exposed.
