
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

- **Styling**: Styles are imported from `./../assets/chat-styles.css`.
- **Logo**: The logo is located at `./../assets/hidini2.webp`.

## Project Structure

- **`src/components`**: Contains Vue components, including the main chat component.
- **`src/assets`**: Static assets like images and stylesheets.
- **`src/main.js`**: Entry point for the Vue application.


Certainly! Below is a complete, formatted section for your README that you can copy and paste to describe the server-side functionality of your application.

## Server

The server is built using Flask and serves as the backend for the Hudini application. It handles prompt submissions, generates responses using the Llama model, and manages previous prompts.

### Key Components

- **Flask Framework**: Provides a web server for handling HTTP requests and responses.
- **Flask-CORS**: Enables Cross-Origin Resource Sharing (CORS) to allow requests from the frontend running on a different domain or port.
- **Llama Model Integration**: Uses the `llama_cpp` library to generate responses based on user prompts.

### Important Files

- **`test.py`**: Main server file that initializes the Flask app, sets up routes, and manages the Llama model.
- **`prompts.json`**: File used to store and retrieve user prompts across server restarts.

### API Endpoints

#### `GET /`

Renders the homepage of the application.

#### `POST /generate`

- **Description**: Receives a user prompt, validates it, and prepares it for response generation.
- **Request Body**: JSON object containing the prompt.
  ```json
  {
    "prompt": "Your input text here"
  }


### Important Files

- **`test.py`**: Main server file that initializes the Flask app, sets up routes, and manages the Llama model.
- **`prompts.json`**: File used to store and retrieve user prompts across server restarts.

### Installing the Llama Model

To use the Llama model, you need to download it from Hugging Face. Follow these steps to set up the model in the correct path:

1. **Install Hugging Face CLI**: Ensure you have the Hugging Face CLI installed. You can install it via pip:

```bash
pip install huggingface-hub
```


- **Responses**:
    - `200 OK`: Prompt received successfully.
    - `400 Bad Request`: No prompt provided.
    - `500 Internal Server Error`: Error processing the prompt.

#### `GET /stream`

- **Description**: Streams generated text based on the last received prompt using server-sent events (SSE).
- **Responses**:
    - `200 OK`: Begins streaming text tokens.
    - `400 Bad Request`: No prompt available for streaming.
    - `500 Internal Server Error`: Error during text generation.

#### `GET /load_prompts`

- **Description**: Returns a list of previously saved prompts.
- **Responses**:
    - `200 OK`: Returns an array of prompts stored in `prompts.json`.

#### `POST /save_prompt`

- **Description**: Saves a new prompt to the server.
- **Request Body**: JSON object with the prompt text.
  ```json
  {
    "prompt": "Your input text here"
  }
  ```
- **Responses**:
    - `200 OK`: Prompt saved successfully, returns the prompt ID.
    - `400 Bad Request`: No prompt provided.
    - `500 Internal Server Error`: Error saving the prompt.

#### `DELETE /delete_prompt/<string:id>`

- **Description**: Deletes a specific prompt by its unique ID.
- **Responses**:
    - `200 OK`: Prompt deleted successfully.
    - `404 Not Found`: Prompt ID not found.
    - `500 Internal Server Error`: Error deleting the prompt.

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

### Configuration

- **Model Path**: The Llama model is loaded from a specified path. Update the model path in `test.py` to point to your model location.
  ```python
  llm_wrapper = LlamaWrapper("C:\\projects\\llama.cpp\\models\\custom\\llama-2-7b-chat.Q4_K_M.gguf")
  ```

### Logging

The server uses Python's `logging` module to record server activity, which helps in debugging and monitoring server operations. Logs are printed to the console with information about requests, responses, and any errors encountered.

### Error Handling

The server includes error handling for common issues like missing prompts, file access errors, and model processing failures. It logs detailed error messages and stack traces for further investigation.

---

This section provides an overview of how to set up, run, and interact with the server component of the Hudini application. If you have any questions or encounter issues, refer to the logs or contact the development team for support.
```

### Instructions

- **Copy the Markdown**: Copy the entire section above.
- **Paste into README**: Place it in your `README.md` file under a section titled "Server" or where it fits best within your documentation.

This description provides an overview of the server's capabilities, endpoints, setup instructions, and configuration options, giving users and developers the information needed to understand and work with the backend of your application.

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


### Key Points

- **Introduction**: Provides a concise overview of what Hudini is and its main functionality.
- **Features**: Highlights the main features of the application.
- **Getting Started**: Instructions on how to set up and run the application locally.
- **Usage**: Explains how to use the application once it's running.
- **API Endpoints**: Lists the backend server endpoints for reference.
- **Project Structure**: Briefly outlines the directory structure.
- **Contributing**: Guidelines for contributing to the project.
- **License**: Specifies the project's license.
- **Contact**: Provides contact information for questions or support.

Feel free to adjust the content based on specific details of your project, such as the exact usage of endpoints, additional setup steps, or particular contribution guidelines.

