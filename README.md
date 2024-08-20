Here's an updated version of your README with an added **Inhaltsverzeichnis** (Table of Contents) that includes links to each section:

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
    - [Manual Start](#manual-start)
- [Access Points](#access-points)
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
ANACONDA_ENV_NAME=aider-ollama
SERVER_URL=http://localhost:5000
PROJECT_MODEL_PATH=C:\\projects\\llama.cpp\\models\\custom\
PROJEKT_ROOT=C:\projects\llama.cpp\projects\src\llama-cpp-chat\src
API_KEY_OPEN_AI=your-openai-api-key-here
PROJECT_FRONTEND_DIRECTORY=C:\\projects\\llama.cpp\\projects\\src\\llama-cpp-chat\\src\\frontend\
DATABASE_URL=postgresql://username:password@localhost:5432/hudini
```

Then, create the Anaconda environment using the name from the `ANACONDA_ENV_NAME` variable:

```bash
conda create --name aider-ollama python=3.8
```

Activate the environment:

```bash
conda activate aider-ollama
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
- Create a new database for the project:

  ```postgresql
  CREATE DATABASE hudini;
  ```

- Create a user and assign it to the database:

  ```postgresql
  CREATE USER your_username WITH PASSWORD 'your_password';
  GRANT ALL PRIVILEGES ON DATABASE hudini TO your_username;
  ```

### 5. Configure `.env.local`

Ensure that your `.env.local` file is properly configured with all the necessary environment variables. Here is an example:

```plaintext
ANACONDA_ENV_NAME=aider-ollama
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

### Manual Start

If you prefer to start each service manually, follow these steps:

1. **Backend Server:**

   Navigate to the backend directory and start the server:

   ```bash
   cd src/server
   python run.py
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

## Running Backend Tests

The test suite for Hudini's backend is located in the `src/backend/tests` directory. These tests ensure that all API endpoints are functioning correctly. To run the backend tests, follow these steps:

1. **Activate your virtual environment** (if you're using one).

2. **Ensure the backend server is running.** If it's not, start it in a separate terminal:

   ```bash
   cd src/server
   python run.py
   ```

3. **Navigate to the test directory:**

   ```bash
   cd src/server/tests


   ```

4. **Run the tests:**

   ```bash
   pytest
   ```

5. **Test Output:**
   After running the tests, pytest will display a summary of the results. A successful test run will look like this:

   ```
   ============================= test session starts ==============================
   ...
   =========================== 5 passed in 1.23s ============================
   ```

   If a test fails, pytest will provide detailed output indicating which tests failed and why.

### Running Specific Tests

You can run specific tests by using the `-k` option followed by the name of the test:

```bash
pytest -k "test_model_loading"
```

### Understanding Test Results

Test results will include information about which tests passed or failed. If a test fails, pytest will show a traceback and a detailed error message to help diagnose the issue.

## Frontend Tests

The frontend tests for Hudini are located in the `src/frontend/tests` directory. These tests ensure that the Vue components and frontend functionality are working correctly. To run the frontend tests using `vitest`, follow these steps:

### Installing Necessary Packages

Ensure that you have the required testing dependencies installed. You may need to install `vitest`, `@vue/test-utils`, and any other testing-related packages:

```bash
npm install --save-dev vitest @vue/test-utils vue-i18n ant-design-vue
```

### Running the Tests

To execute the frontend tests, run:

```bash
npx vitest run
```

### Example Test Code

Here is an example of a frontend test written using `vitest` and `@vue/test-utils` for the `ChatForm.vue` component:

```javascript
import { mount } from '@vue/test-utils';
import ChatForm from './ChatForm.vue';
import { createI18n } from 'vue-i18n';
import Antd from 'ant-design-vue'; // Import Ant Design Vue
import { nextTick } from 'vue';
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'; // Import vitest functions

// Mock window.matchMedia
window.matchMedia = window.matchMedia || function () {
    return {
        matches: false,
        addListener: function () { },
        removeListener: function () { }
    };
};

// Mock EventSource
global.EventSource = vi.fn(() => ({
    onmessage: null,
    onerror: null,
    close: vi.fn(),
}));

// Create a basic i18n setup
const messages = {
    en: {
        hudini_title: 'Hudini - CPU Magician on SLM',
        select_model: 'Select Model',
        enter_prompt: 'Enter your prompt here...',
        send_button: 'Send',
        delete: 'Delete',
        your_response: 'Your response will appear here',
        copied_to_clipboard: 'Prompt copied to clipboard',
        failed_to_copy: 'Failed to copy prompt',
        prompt_deleted: 'Prompt deleted',
        previous_prompts: 'Previous Prompts',
        no_prompts: 'No prompts saved yet',
        failed_to_load_prompts: 'Failed to load prompts',
    }
};

const i18n = createI18n({
    legacy: false,
    locale: 'en',
    fallbackLocale: 'en',
    messages,
});

// Mock the fetch API globally
global.fetch = vi.fn((url) => {
    if (url.includes('/get_models')) {
        return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({
                local_models: ['Local Model 1', 'Local Model 2'],
                openai_models: ['OpenAI Model 1', 'OpenAI Model 2']
            }),
        });
    } else if (url.includes('/generate')) {
        return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({ result: 'Generated response' }),
        });
    } else if (url.includes('/save_prompt')) {
        return Promise.resolve({ ok: true });
    } else if (url.includes('/load_prompts')) {
        return Promise.resolve({
            ok: true,
            json: () => Promise.resolve([]),
        });
    }
});

describe('ChatForm.vue', () => {
    let wrapper;

    beforeEach(() => {
        wrapper = mount(ChatForm, {
            global: {
                plugins: [i18n, Antd], // Register Ant Design Vue globally
            },
        });
    });

    afterEach(() => {
        vi.clearAllMocks(); // Clears mock state between tests
        if (wrapper) {
            wrapper.unmount();
        }
    });

    it('renders correctly and displays the title', () => {
        expect(wrapper.text()).toContain('Hudini - CPU Magician on SLM');
    });

    it('loads models on mount', async () => {
        await nextTick();
        expect(global.fetch).toHaveBeenCalledWith(expect.stringContaining('/get_models'));

        // Check that the models were loaded correctly
        expect(wrapper.vm.localModels.length).toBeGreaterThan(0);
        expect(wrapper.vm.openaiModels.length).toBeGreaterThan(0);
    });

    it('updates the response area when a prompt is submitted', async () => {
        // Wait until the models are loaded and the DOM updates
        await nextTick();
        await nextTick();

        // Set selectedModel and prompt by simulating user input
        const select = wrapper.find('input.ant-select-selection-search-input'); // Adjust the selector based on how a-select renders
        await select.setValue('Local Model 1');
        const textarea = wrapper.find('textarea');
        await textarea.setValue('Test Prompt');

        // Simulate clicking the send button
        const sendButton = wrapper.find('.send-button');
        await sendButton.trigger('click');
        await nextTick();

        // Log the fetch calls to diagnose extra calls
        fetch.mock.calls.forEach((call, index) => {
            console.log(`Fetch Call ${index + 1}: ${call[0]}`);
        });

        // Verify that the response area updated
        expect(wrapper.find('#response').text()).toContain('Your response will appear here');
    });

    it('increments updateTrigger when prompt is saved', async () => {
        // Wait until the models are loaded and the DOM updates
        await nextTick();
        await nextTick();

        // Set selectedModel and prompt by simulating user input
        const select = wrapper.find('input.ant-select-selection-search-input');
        await select.setValue('Local Model 1');
        const textarea = wrapper.find('textarea');
        await textarea.setValue('Test Prompt');

        // Simulate clicking the send button
        const sendButton = wrapper.find('.send-button');
        await sendButton.trigger('click');
        await nextTick();

        // Expect updateTrigger to increment
        expect(wrapper.vm.updateTrigger).toBe(1);
    });
});
```

---

With this updated README, users will be able to quickly navigate to any section they need and find detailed information about setting up, running, and testing the Hudini project.
