Certainly! Here is an updated version of your README document for the Hudini application, including the PowerShell script to run the Ollama server and open the link to `http://localhost:11434/`:

---


# Hudini - CPU Magician on SLM

![Hudini Logo](./src/assets/hidini2.webp)

### JUST FOR TESTING PURPOSES. DO NOT USE IT IN PRODUCTION!

Hudini is an interactive chat interface designed to work with CPU magic on SLM. This application allows users to input prompts and receive responses in real time. The application also manages previous prompts, allowing users to easily revisit and delete them.

## Features

- **Interactive Chat Interface**: Type your prompt in the textarea and send it to receive responses.
- **Real-Time Responses**: Receive instant feedback on your inputs.
- **Previous Prompts Management**: Save, load, and delete previous prompts.
- **Responsive UI**: Designed with a modern, user-friendly interface.

## Getting Started

### Prerequisites

Ensure you have the following software installed on your machine:

- [Node.js](https://nodejs.org/) (v12 or later)
- [Vue CLI](https://cli.vuejs.org/) (optional for scaffolding Vue projects)
- [Git](https://git-scm.com/) (for version control)

### Installation

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd hudini
   ```

2. **Install dependencies:**

   ```bash
   npm install
   ```

3. **Run the development server:**

   ```bash
   npm run serve
   ```

   This will start the application on `http://localhost:8080/`.

### Running the Backend Server

To enable prompt saving and generation functionality, you need a backend server. The server endpoints used are:

- `http://localhost:5000/load_prompts` for loading prompts.
- `http://localhost:5000/generate` for generating responses.
- `http://localhost:5000/save_prompt` for saving prompts.
- `http://localhost:5000/delete_prompt/:id` for deleting prompts.

### PowerShell Script to Run Ollama and Open URL

To run the Ollama server and open the link in your default browser, use the following PowerShell script:

Open Script and change your path to ollama.exe

```powershell
cd <project_dir>/bin
.\ServeDirectory_Background.ps1
```

### Usage

1. **Enter a Prompt**: Type your prompt into the textarea and press "Enter" or click the "Send" button to receive a response.
2. **Manage Prompts**: View, select, and delete previous prompts from the "Previous Prompts" section.
3. **Live Response Streaming**: See your response appear in real-time within the chat area.

### API Endpoints

- **GET `/load_prompts`**: Retrieve all previous prompts.
- **POST `/generate`**: Send a prompt to the server to receive a response.
- **POST `/save_prompt`**: Save a new prompt to the database.
- **DELETE `/delete_prompt/:id`**: Remove a prompt by its ID.

### Configuration

- **Styling**: Styles are imported from `./src/assets/chat-styles.css`.
- **Logo**: The logo is located at `./src/assets/hidini2.webp`.

## Project Structure

- **`src/components`**: Contains Vue components, including the main chat component.
- **`src/assets`**: Static assets like images and stylesheets.
- **`src/main.js`**: Entry point for the Vue application.

## Server

The server is built using Flask and serves as the backend for the Hudini application. It handles prompt submissions, generates responses using the Llama model, and manages previous prompts.

### Key Components

- **Flask Framework**: Provides a web server for handling HTTP requests and responses.
- **Flask-CORS**: Enables Cross-Origin Resource Sharing (CORS) to allow requests from the frontend running on a different domain or port.
- **Llama Model Integration**: Uses the `llama_cpp` library to generate responses based on user prompts.

### Important Files

- **`test.py`**: Main server file that initializes the Flask app, sets up routes, and manages the Llama model.
- **`prompts.json`**: File used to store and retrieve user prompts across server restarts.

### Installing the Llama Model

To use the Llama model, you need to download it from Hugging Face. Follow these steps to set up the model in the correct path:

#### Option 1: Install Using Hugging Face CLI

1. **Install Hugging Face CLI**: Ensure you have the Hugging Face CLI installed. You can install it via pip:

   ```bash
   pip install huggingface-hub
   ```

2. **Login to Hugging Face**: Use the CLI to log in to your Hugging Face account. Create an account if you don't have one.

   ```bash
   huggingface-cli login
   ```

3. **Download the Model**: Run the following command to download the LLaMA-7b model to the specified directory:

   ```bash
   huggingface-cli download TheBloke/LLaMA-7b-GGUF llama-7b.Q4_K_M.gguf --local-dir C:/projects/llama-cpp --local-dir-use-symlinks False
   ```

   This command will place the model file in `C:/projects/llama-cpp`.

4. **Verify the Model Path**: Ensure your server code points to this model path:

   ```python
   llm_wrapper = LlamaWrapper("C:\\projects\\llama-cpp\\llama-7b.Q4_K_M.gguf")
   ```

#### Option 2: Install Using Conda

1. **Install Conda**: Ensure you have Conda installed. If not, download and install [Anaconda](https://www.anaconda.com/products/distribution#download-section) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html).

2. **Create a New Conda Environment**: Create and activate a new environment:

   ```bash
   conda create --name llama_env python=3.9
   conda activate llama_env
   ```

3. **Install Required Packages**:

   ```bash
   conda install flask flask-cors
   pip install llama-cpp-python huggingface-hub
   ```

4. **Download the Model**: Use the Hugging Face CLI command as described in Option 1 to download the model to `C:/projects/llama-cpp`.

5. **Verify the Model Path**: Ensure your server code points to this model path:

   ```python
   llm_wrapper = LlamaWrapper("C:\\projects\\llama-cpp\\llama-7b.Q4_K_M.gguf")
   ```

### Running the Server

1. **Ensure Dependencies Are Installed**: Install required Python packages using pip.

   ```bash
   pip install flask flask-cors llama-cpp-python
   ```

2. **Start the Server**: Run the Flask application.

   ```bash
   python test.py
   ```

   The server will start on `http://0.0.0.0:5000` with debug mode enabled.

### Logging

The server uses Python's `logging` module to record server activity, which helps in debugging and monitoring server operations. Logs are printed to the console with information about requests, responses, and any errors encountered.

### Error Handling

The server includes error handling for common issues like missing prompts, file access errors, and model processing failures. It logs detailed error messages and stack traces for further investigation.

## Contributing

1. Fork the repository.
2. Create your feature branch: `git checkout -b my-new-feature`.
3. Commit your changes: `git commit -m 'Add some feature'`.
4. Push to the branch: `git push origin my-new-feature`.
5. Submit a pull request.

## License

This project is licensed under the MIT License.

## Contact

For further information or inquiries, please contact [Your Name] at [your.email@example.com].

---

### Key Improvements

- **Structure**: The document has been restructured to have clear headings and subheadings for easy navigation.
- **Redundancy**: Removed redundant sections and combined related content for clarity.
- **Consistency**: Consistent formatting and

language used throughout the document.
- **Instructions**: Clearer instructions and descriptions provided for setup and configuration steps.

Feel free to update sections such as contact details, repository URL, and any additional information specific to your project.
