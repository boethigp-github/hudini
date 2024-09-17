/**
 * The base URL of the API server.
 *
 * @constant {string}
 */
const API_BASE_URL = import.meta.env.SERVER_URL || 'http://localhost:8000';

/**
 * Converts a JavaScript object to a Markdown string representation.
 * The Markdown string includes the keys and corresponding values of the object.
 * The object's properties are indented based on the depth of the nested objects.
 * If a property's value is an object, it will be recursively converted to a Markdown string.
 * If a property's value is a primitive type, it will be converted to a Markdown code block.
 *
 * @param {Object} obj - The object to be converted to Markdown.
 * @param {string} [indent=''] - The indentation string used for nested objects.
 * @returns {string} The Markdown string representation of the object.
 */
export const objectToMarkdownString = (obj, indent = '') => {
    if (typeof obj !== 'object' || obj === null) {
        return `\`${String(obj)}\``;
    }

    let markdown = '';
    for (const [key, value] of Object.entries(obj)) {
        markdown += `${indent} ${key}: `;
        if (typeof value === 'object' && value !== null) {
            markdown += '\n' + objectToMarkdownString(value, indent + '  ');
        } else {
            markdown += `\`${String(value)}\``;
        }
        markdown += '\n';
    }
    return markdown.trim();
};
/**
 * Sends a request to call a tool with the given content.
 *
 * @param {object} content - The content containing the tool and its parameters.
 * @param {string} content.tool - The name of the tool to call.
 * @param {object} content.parameters - The parameters required for the tool.
 * @returns {Promise<object>} - A promise that resolves to the response JSON object.
 * @throws {Error} - Throws an error if the request to call the tool fails.
 */
export const callTool = async (content) => {
    try {
        const requestBody = {
            tool: content.tool,
            parameters: content.parameters
        }
        console.log("callTool:", requestBody);

        const response = await fetch(`${API_BASE_URL}/tools/call`, {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody),
        });

        if (!response.ok) {
            throw new Error(`Failed to call tool: ${requestBody}, status: ${response.status}`);
        }


        return await response.json();
    } catch (error) {
        console.error('Error calling tool:', error);
        throw error;
    }
};

/**
 * Parses the content of a JSON object from the given input string.
 *
 * @param {string} input - The input string containing a JSON object.
 * @returns {object|null} - The parsed JSON object or null if no JSON content is found or if there is a parsing error.
 */
export const parseCallContent = (input) => {
    // Regex to match a JSON object, accounting for possible whitespace
    const regex = /\s*(\{[\s\S]*\})\s*/;

    // Extract the content
    const match = input.match(regex);

    if (match && match[1]) {
        try {
            // Attempt to parse the extracted content as JSON
            const jsonContent = JSON.parse(match[1]);
            console.log("jsonContent", jsonContent);
            return jsonContent;
        } catch (error) {
            console.error("Error parsing JSON:", error);
            return null;
        }
    } else {
        console.log("No JSON content found");
        return null;
    }
};

/**
 * Asynchronously processes the given content by making a tool call.
 * If the processed content or the processed tool is missing, the content is returned as is.
 * The response object is logged to the console.
 * The response object is converted to a Markdown string.
 * The original JSON in the content is replaced with the Markdown string, removing the ```json prefix.
 * Any error that occurs during the process is logged to the console.
 *
 * @param {string} content - The content to be processed
 * @returns {string} - The processed content
 */
export const processToolCalling = async (content) => {
    let processedContent = parseCallContent(content);

    if (!processedContent || !processedContent.tool) {
        return content;
    }

    try {
        let response = await callTool(processedContent);
        if (!response) {
            return content;
        }

        console.log("response", response);

        // Convert the response object to a Markdown string
        const markdownString = objectToMarkdownString(response);

        // Replace the original JSON in the content with the Markdown string, removing the ```json prefix
        return "<div>" + content.replace(/```json\s*\{[\s\S]*\}\s*/, markdownString).replace(/```/g, "") + "</div>";
    } catch (error) {
        console.error("Error processing tool call:", error);
    }

    return content;
};

