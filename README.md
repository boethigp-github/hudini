Creating a README for your project is essential for providing context and instructions for other developers (or yourself in the future). Below is a template for a `README.md` file tailored to your Vue.js project:

```markdown
# Hudini - CPU Magician on SLM

![Hudini Logo](./../assets/hidini2.webp)

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

```

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
