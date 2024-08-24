Sure! Here's the complete README with the updated **Directory Structure** section reflecting your new directory structure:

---

# Hudini - CPU Magician on SLM

![Hudini Logo](src/client/vue/assets/hidini2.webp)

**CAUTION: FOR TESTING PURPOSES ONLY. NOT FOR PRODUCTION USE.**

Hudini is an interactive chat interface that works with CPU magic on SLM, allowing real-time prompt input and response generation.

## Inhaltsverzeichnis

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Setup](#setup)
    - [1. Clone the Repository and Install Dependencies](#1-clone-the-repository-and-install-dependencies)
    - [2. Create the Anaconda Environment](#2-create-the-anaconda-environment)
    - [3. Install Required Python Packages](#3-install-required-python-packages)
    - [4. Set Up PostgreSQL Database](#4-set-up-postgresql-database)
    - [5. Configure `.env.local`](#5-configure-envlocal)
    - [6. Install the Llama Model](#6-install-the-llama-model)
- [Running the Application](#running-the-application)
    - [Automated Start (All Services)](#automated-start-all-services)
    - [Manual Start with `flask run`](#manual-start-with-flask-run)
- [Access Points](#access-points)
- [Caching](#caching)
    - [How Caching Works](#how-caching-works)
    - [Clearing the Cache](#clearing-the-cache)
- [Directory Structure](#directory-structure)
- [Running Backend Tests](#running-backend-tests)
    - [Running Specific Tests](#running-specific-tests)
    - [Understanding Test Results](#understanding-test-results)
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
- [Python](https://www.python.org/) (3.7+)
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

You need to create an Anaconda environment with the name specified in the `.env.local` file. First, ensure that the `.env.local` file contains the environment name:

**Example `.env.local` content:**

```plaintext
ANACONDA_ENV_NAME=hudini
SERVER_URL=http://localhost:5000
PROJECT_MODEL_PATH=C:\\projects\\llama.cpp\\models\\custom\
PROJEKT_ROOT=C:\projects\llama.cpp\projects\src\llama-cpp-chat\src
API_KEY_OPEN_AI=your-openai-api-key-here
PROJECT_FRONTEND_DIRECTORY=C:\\projects\\llama.cpp\\projects\\src\\llama-cpp-chat\\src\\frontend\
DATABASE_URL=postgresql://username:password@localhost:5432/hudini
```

Then, create the Anaconda environment using the name from the `ANACONDA_ENV_NAME` variable:

```bash
conda create --name hudini python=3.8
```

Activate the environment:

```bash
conda activate hudini
```

### 3. Install Required Python Packages

The `requirements.txt` file is located at `src/backend/requirements.txt`. To install the required Python packages, navigate to this directory and run:

```bash
cd src/server
pip install -r requirements.txt
```

### 4. Set Up PostgreSQL Database

**Step 4.1: Install PostgreSQL**

- Download and install PostgreSQL from the [official website](https://www.postgresql.org/download/).

**Step 4.2: Create a Database**

- Open the PostgreSQL command line or a tool like pgAdmin.
- To ensure you start with a clean setup, you may drop the existing `hudini` database (if it exists) and then create a new one using the following SQL commands:

```sql
-- Drop the database if it exists
DROP DATABASE IF EXISTS hudini;

-- Create the new database
CREATE DATABASE hudini
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'German_Germany.1252'
    LC_CTYPE = 'German_Germany.1252'
    LOCALE_PROVIDER = 'libc'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;
```

- Create a user and assign it to the database (replace `your_username` and `your_password` with your desired values):

  ```sql
  CREATE USER your_username WITH PASSWORD 'your_password';
  GRANT ALL PRIVILEGES ON DATABASE hudini TO your_username;
  ```

**Step 4.3: Create the `prompts` Table**

- After setting up the database, you can create the `prompts` table using the following SQL commands:

```sql
-- Drop the prompts table if it exists
DROP TABLE IF EXISTS public.prompts;

-- Create the prompts table
CREATE TABLE IF NOT EXISTS public.prompts
(
    id uuid NOT NULL,
    prompt text COLLATE pg_catalog."default" NOT NULL,
    "timestamp" timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "user" character varying(30) COLLATE pg_catalog."default",
    status character varying(30) COLLATE pg_catalog."default",
    CONSTRAINT prompts_pkey PRIMARY KEY (id)
)
TABLESPACE pg_default;

-- Set the owner of the prompts table
ALTER TABLE IF EXISTS public.prompts
    OWNER to postgres;
```

This command creates the `prompts` table in the `public` schema of the `hudini` database with the following columns:

- `id`: A UUID that serves as the primary key.
- `prompt`: A text field to store the prompt.
- `timestamp`: A timestamp that records when the prompt was created, defaulting to the current timestamp.
- `user`: A character varying field for storing the user associated with the prompt.
- `status`: A character varying field for storing the status of the prompt.

### 5. Configure `.env.local`

Ensure that your `.env.local` file is properly configured with all the necessary environment variables. Here is an example:

```plaintext
ANACONDA_ENV_NAME=hudini
SERVER_URL=http://localhost:5000
PROJECT_MODEL_PATH=C:\\projects\\llama.cpp\\models\\custom\
PROJEKT_ROOT=C:\projects\llama.cpp\projects\src\llama-cpp-chat\src
API_KEY_OPEN_AI=your-openai-api-key-here
PROJECT_FRONTEND_DIRECTORY=C:\\projects\\llama.cpp\\projects\\src\\llama-cpp-chat\\src\\frontend\
DATABASE_URL=postgresql://username:password@localhost:5432/hudini
```

### 6. Install the Llama Model

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

### Manual Start with `flask run`

If you prefer to start each service manually, you can now start the backend server using `flask run`. Follow these steps:

1. **Backend Server:**

   Navigate to the server directory and start the server:

   ```bash
   cd src/server
   flask run
   ```

2. **Frontend Development Server:**

   Navigate to the frontend directory and start the development server:

   ```bash
   cd client
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

## Caching

### How Caching Works

Hudini uses a caching mechanism to store and retrieve data quickly, improving the performance of the application