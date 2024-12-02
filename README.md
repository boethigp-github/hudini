To adjust the README documentation to reflect the use of `bigint` for `user` and `id` in your database tables, here is the updated documentation:

---

# Hudini - CPU Magician on SLM

![Hudini Logo](/client/vue/assets/Fhudini-logo.webp)

**CAUTION: FOR TESTING PURPOSES ONLY. NOT FOR PRODUCTION USE.**

Hudini is an interactive chat interface that works with CPU magic on SLM, allowing real-time prompt input and response generation.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Setup](#setup)
  - [1. Clone the Repository and Install Dependencies](#1-clone-the-repository-and-install-dependencies)
  - [2. Create the Anaconda Environment](#2-create-the-anaconda-environment)
  - [3. Install Required Python Packages](#3-install-required-python-packages)
  - [4. Set Up PostgreSQL Database](#4-set-up-postgresql-database)
  - [4_1. Activate LLM Provider](#4_1-activate-llm-provider)
  - [5. Configure Environment Variables](#5-configure-environment-variables)
  - [6. Install the Llama Model](#6-install-the-llama-model)
- [Running the Application](#running-the-application)
  - [Manual Start with `fastapi run`](#manual-start-with-fastapi-run)
- [Access Points](#access-points)
- [Caching](#caching)
  - [How Caching Works](#how-caching-works)
  - [Clearing the Cache](#clearing-the-cache)
- [Directory Structure](#directory-structure)
- [Running Backend Tests](#running-backend-tests)
  - [Running Specific Tests](#running-specific-tests)
  - [Understanding Test Results](#understanding-test-results)
  - [Load Tests](#loadtests) 
- [Frontend Tests](#frontend-tests)
  - [Installing Necessary Packages](#installing-necessary-packages)
  - [Running the Tests](#running-the-tests)
  - [Example Test Code](#example-test-code)

## Features

- Interactive chat interface with real-time responses
- Previous prompts management (save, load, delete)
- Responsive UI design
- API documentation with Swagger
- Interactive API exploration with Swagger UI

## Prerequisites

- [Node.js](https://nodejs.org/) (v12+)
- [Git](https://git-scm.com/)
- [Python](https://www.python.org/) (3.9+)
- [Anaconda](https://www.anaconda.com/) (for managing Python environments)
- [PostgreSQL](https://www.postgresql.org/) (for database management)
- [Hugging Face CLI](https://huggingface.co/docs/huggingface_hub/quick-start) (for downloading models)

## Setup

### 1. Clone the Repository and Install Dependencies

```bash
git clone <repository-url>
cd llama-cpp-chat/client
npm install
```

### 2. Create the Anaconda Environment

You need to create an Anaconda environment with the name specified in the environment variables. First, ensure that the environment variables file contains the environment name:

**Example environment variables content:**

```plaintext
## Startupscripts
ANACONDA_ENV_NAME=hudini

SERVER_URL=http://localhost:80
PROJECT_MODEL_PATH=C:\\projects\\llama.cpp\\models\\custom\

PROJEKT_ROOT=C:\projects\llama.cpp\projects\src\llama-cpp-chat\src
API_KEY_OPEN_AI=
API_KEY_ANTHROPIC=
API_KEY_GOOGLE_AI=
APP_ACTIVE_PROVIDER=OPEN_AI
PROJECT_FRONTEND_DIRECTORY=C:\\projects\\llama.cpp\\projects\\src\\llama-cpp-chat\\src\\frontend\
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost/hudini
DATABASE_URL_SYNC=postgresql+psycopg2://postgres:postgres@localhost/hudini
APP_TIMEZONE=Europe/Berlin
APP_DEBUG=False
APP_ENV=development
APP_Testing=False
APP_LOG_LEVEL=DEBUG
APP_PROJECT_NAME=HUDINI
APP_CORS_ORIGIN=http://localhost:5173,https://editor.swagger.io
APP_CACHE=C:\projects\hudini\server\var\cache
APP_STORAGE=C:\projects\hudini\server\storage
DB_SQL_ECHO=False
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=5
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=1800
DB_USE_NULL_POOL=False
SOCIALMEDIA_USER='[{
  "provider": "telegram",
  "api_id": "",
  "displayname": "hudini",
  "api_hash": "",
  "phone_number": "",
  "password": "",
  "groups": [
      "@hudinitests"
    ]
}]'
```

Then, create the Anaconda environment using the name from the `ANACONDA_ENV_NAME` variable:

```bash
conda create --name hudini python=3.9
```

Activate the environment:

```bash
conda activate hudini
```

### 3. Install Required Python Packages

The `requirements.txt` file is located at `src/server/requirements.txt`. To install the required Python packages, navigate to this directory and run:

```bash
cd src/server
pip install -r requirements.txt
```

Here's the updated PostgreSQL database setup section in Markdown format:

---

### 4. Set Up PostgreSQL Database



Download and install PostgreSQL from the [official website](https://www.postgresql.org/download/).

#### Step 4.2: Create a Database

Open the PostgreSQL command line or a tool like pgAdmin. To create a new database, use the following SQL command:

```sql
CREATE DATABASE hudini;
```

#### Step 4.3: Apply Database Migrations

1. Navigate to the database migration directory:

    ```bash
    cd <project_root>/server/app/db
    ```

2. To reset your database to its initial state and then apply all migrations, use Alembic:

    ```bash
    alembic downgrade base
    alembic upgrade head
    ```

This will ensure that all tables and schemas are created with the correct `bigint` types for `user` and `id`.

---

## 4_1. Activate LLM Provider

Hudini allows you to integrate with multiple AI model providers (such as OpenAI, Anthropic, and Google AI). You can control which providers are active by setting the `APP_ACTIVE_PROVIDER` environment variable in the `.env.local` file.

### How to Activate Providers

The `APP_ACTIVE_PROVIDER` variable is a comma-separated list of the providers you want to activate. You can include any combination of the following providers:

- `OPEN_AI`
- `ANTHROPIC`
- `GOOGLE_AI`

### Example Configuration

To activate multiple providers, add the `APP_ACTIVE_PROVIDER` variable to your `.env.local` file:

```plaintext
APP_ACTIVE_PROVIDER=OPEN_AI,ANTHROPIC,GOOGLE_AI
```

This activates all three providers: OpenAI, Anthropic, and Google AI. Hudini will query models from these providers when a request is made to the `/models` endpoint.

### Deactivating Providers

If you want to limit which providers are active, simply remove the providers you don’t want from the `APP_ACTIVE_PROVIDER` variable. For example, to activate only OpenAI:

```plaintext
APP_ACTIVE_PROVIDER=OPEN_AI
```

In this case, Hudini will only retrieve models from OpenAI when a request is made to the `/models` endpoint.

### No Providers Activated

If no providers are specified in the `.env.local` file, Hudini won’t query any providers and will return an empty list. For example, setting `APP_ACTIVE_PROVIDER` as an empty string:

```plaintext
APP_ACTIVE_PROVIDER=
```


### How to Set Environment Variables in `.env.local`

1. Navigate to the root directory of your project.
2. Open or create the `.env.local` file.
3. Add or modify the `APP_ACTIVE_PROVIDER` variable according to the providers you want to activate.

Example `.env.local` content:

```plaintext
APP_ACTIVE_PROVIDER=OPEN_AI,ANTHROPIC
```

---

This updated section explains how to configure and activate AI providers solely through the `.env.local` file, without mentioning OS-specific environment variable setups.




### 5. Configure Environment Variables

Ensure that your environment variables are properly configured as shown in the earlier example. Replace the placeholder API keys with your actual API keys.

Ah, I misunderstood! You only want to explain the use of environment variables through the `.env.local` file, not through shell commands or OS-specific instructions. Here’s the corrected documentation that focuses solely on the `.env.local` configuration:

---


### 6. Install the Llama Model

To download and install the Llama model, follow these steps:

```bash
huggingface-cli login
huggingface-cli download TheBloke/LLaMA-7b-GGUF llama-7b.Q4_K_M.gguf --local-dir C:/projects/llama-cpp/models/custom --local-dir-use-symlinks False
```

## Running the Application

### Manual Start with `fastapi run`

If you prefer to start each service manually, follow these steps:

1. **Activate the Conda Environment:**

   ```bash
   conda activate hudini
   ```

2. **Backend Server:**

   Navigate to the server directory and start the server:

   ```bash
   cd <project_root>\server
   fastapi run run.py --port=80
   ```

   if you want to start in debug mode and reload
  ```bash 
   run run.py --port=80 --reload
    ```

   This starts the FastAPI application on port 80.

3. **Frontend Development Server:**

   Navigate to the frontend directory and start the development server:

   ```bash
   cd <project_root>\client
   npm run dev
   ```

   This starts the frontend on the default development port (likely 5173).

## Access Points

- **Frontend:** [http://localhost:5173](http://localhost:5173)
- **Backend API:** [http://localhost:80](http://localhost:80)
- **Ollama server:** [http://localhost:11434](http://localhost:11434)
- **Swagger YAML:** [http://localhost:80/swagger.yaml](http://localhost:80/swagger.yaml)
- **Swagger UI:** [http://localhost:80/api/docs](http://localhost:80/api/docs)

## Caching

### How Caching Works

Hudini uses a caching mechanism to store and retrieve data quickly, improving the performance of the application. The cache is typically stored in the directory specified by the `APP_CACHE` environment variable.

### Clearing the Cache

To clear the cache, you can manually delete the contents of the cache directory specified by `APP_CACHE`.

via cli:

```shell
cd <project_root/server/app/cli>
python cache-clear.py 
```

## Directory Structure

Here's a typical directory structure for the Hudini project:

```
hudini/
├── client/                         
├── docs/                           
├── infrastructure/                 
│   ├── database/                   
│   │   ├── migrations/             
│   │   │   ├── __init__.py         
│   │   │   └── alembic.ini         
│   ├── environment/                
│   │   ├── .env.local              
│   │   ├── .env.local.dist         
│   │   └── __init__.py             
│   ├── scripts/                    
│   │   └── python/                 
│   │       └── __init__.py         
│   └── swagger/                    
│       ├── __init__.py             
│       └── swagger.yaml            
├── server/                         
│   ├── app/                        
│   │   ├── adapters/               
│   │   ├── cli/                    
│   │   ├── clients/                
│   │   ├── config/                 
│   │   ├── core/                   
│   │   ├── db/                     
│   │   ├── factory/                
│   │   ├── models/                 
│   │   ├── routers/                
│   │   ├── services/               
│   │   └── utils/                  
│   │       ├── __init__.py         
│   │       └── extensions.py       
│   ├── server/                     
│   │   └── var/                    
│   │       └── cache/              
│   │           ├── cache.db        
│   │           ├── cache.db-shm    
│   │           └── cache.db-wal    
│   └── storage/                    
└── tests/                          
    └── functional/                 
        ├── generation/             
        ├── models/                 
        ├── prompts/                
        └── swagger/                
```

## Running Backend Tests

### Running Specific Tests

To run specific backend tests, you can use `pytest` with test file or function names. Navigate to the `server` directory and run:

```bash
cd <project_root>\server
pytest -k "test_function_name"
```

Replace `"test_function_name"` with the name of the test function or file you want to run.

### Understanding Test Results

After running the tests, `pytest` will display the results, showing which tests passed, failed, or were skipped. Review the output to identify and resolve any issues.

### Running Locust Tests

Locust is used to perform load testing on your backend APIs. Here’s how you can run Locust tests:

1. **Navigate to the Locust Test Directory**

   Navigate to the directory where your `locustfile.py` is located. In your project structure, this is under `tests/functional/models`.

   ```bash
   cd <project_root>\tests\functional\models
   ```

2. **Run Locust**

   To execute the Locust tests, run the following command:

   ```bash
   locust -f locustfile.py
   ```

   This command will start the Locust load testing process, and you can monitor the results through the browser-based interface usually available at `http://localhost:8089`.

### Example Locust Test Script

Here is an example of a Locust test script that performs load testing on your FastAPI backend:

```python
from locust import HttpUser, task, events
from locust.runners import MasterRunner, WorkerRunner, LocalRunner
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_test_users(environment, msg):
    # Example setup logic
    logger.info("Setting up test users")
    # You can initialize test users here, e.g., by making requests to your FastAPI application

class ModelsUser(HttpUser):
    host = "http://localhost:8000"  # Replace with your FastAPI server's address

    @task
    def get_models(self):
        with self.client.get("/models", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
                logger.info("Request succeeded with status 200")
            else:
                response.failure(f"Got unexpected status code: {response.status_code}")
                logger.error(f"Request failed with status code: {response.status_code}")

    def on_start(self):
        # Optional: Perform any setup actions (e.g., authentication) here
        pass

# Event listener to set up the custom message handler
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    if isinstance(environment.runner, MasterRunner) or isinstance(environment.runner, WorkerRunner):
        # Register the custom message handler on the runner
        environment.runner.register_message('test_users', setup_test_users, concurrent=True)
        logger.info("Custom message handler registered")

# Main block to run the test script
if __name__ == "__main__":
    # Create a local runner (single machine)
    runner = LocalRunner(env=None)

    # Optionally: Start the web UI for monitoring
    web_ui = runner.start_web_ui("127.0.0.1", 8089)

    # Register the custom message handler (if not done in `on_test_start`)
    if isinstance(runner, MasterRunner) or isinstance(runner, WorkerRunner):
        runner.register_message('test_users', setup_test_users, concurrent=True)
        logger.info("Custom message handler registered in main block")

    # Start the test
    logger.info("Starting the test")
    runner.start(1, spawn_rate=1)
    runner.greenlet.join()

    # Stop the web UI after the test
    if web_ui:
        web_ui.stop()
        logger.info("Web UI stopped")
```

## Frontend Tests

### Installing Necessary Packages

Before running frontend tests, ensure that all dependencies are installed:

```bash
cd <project_root>\client
npm install
```

### Running the Tests

To run the frontend tests, use the following command:

```bash
npm run test
```

### Example Test Code

Here’s an example of how you might write a test for a component in your frontend:

```javascript
import { render, screen } from '@testing-library/vue';
import MyComponent from '@/components/MyComponent.vue';

test('renders the component correctly', () => {
  render(MyComponent);
  const element = screen.getByText('Expected Text');
  expect(element).toBeInTheDocument();
});
```

## Caching

### How Caching Works

Hudini uses a caching mechanism to store and retrieve data quickly, improving the performance of the application. The cache is typically stored in the directory specified by the `APP_CACHE` environment variable.

### Clearing the Cache

To clear the cache, you can manually delete the contents of the cache directory specified by `APP_CACHE`.

---

This README documentation now provides a comprehensive guide on how to set up, run, and test the Hudini project, with the necessary adjustments for using `bigint` for `user` and `prompt_id`.


## Embeddings
put your pdfs in /server/storage/pdfs
Create embeddings:
```shell
cd server/app/cli
python  pdf_embeddings_cli.py C:/projects/hudini/server/storage/pdfs --output embeddings.pkl --metadata-output metadata.pkl
```

save embeddings to faiss
```shell
cd server/app/cli
python  save_vectors_to_faiss.py
```

ask chatgpt about the content
```shell
python  ask_gpt_with_faiss_search.py
```
ssh login

```shell
ssh -l root 78.47.242.59
```
### Ansible install
```shell
cd infrastructure/environment/
ansible-playbook playbook_install_hudini.yml
```