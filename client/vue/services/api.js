const API_BASE_URL = import.meta.env.SERVER_URL || 'http://localhost:8000';

/**
 *
 * @param stream_url
 * @param generationRequest
 * @param onChunk
 * @param buffer
 * @param responses
 * @param onError
 * @param onComplete
 * @returns {Promise<void>}
 */
export const stream = async (stream_url, generationRequest, onChunk, buffer, responses, onError, onComplete) => {
    try {
        const response = await fetch(`${API_BASE_URL}${stream_url}`, {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(generationRequest),
        });

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const {done, value} = await reader.read();
            if (done) {
                onComplete();
                break;
            }
            const chunk = decoder.decode(value);
            onChunk(chunk, buffer, responses);
        }
    } catch (error) {
        console.error('Error in stream:', error);
        onError(error);
    }
};


/**
 * Fetches available models from the server.
 * @returns {Promise<Object>} A promise that resolves to an object containing local and OpenAI models.
 */
export const getModels = async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/models`, {
            credentials: 'include',
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching models:', error);
        throw error;
    }
};

/**
 * Saves a prompt to the server.
 * @param {Object} promptRequest - The prompt data to save.
 * @returns {Promise<Object>} A promise that resolves to the server's response.
 */
export const createPrompt = async (promptRequest) => {
    try {
        const response = await fetch(`${API_BASE_URL}/prompts`, {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(promptRequest),
        });

        // Ensure response is defined and has an 'ok' property
        if (!response || !response.ok) {
            throw new Error(`HTTP error! status: ${response ? response.status : 'undefined'}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Error saving prompt:', error);
        throw error;
    }
};

/**
 * Sends the collected responses to the /usercontext endpoint.
 * @param {object} userContextList - Array of response objects to send.
 * @param callback
 * @returns {Promise<void>} A promise that resolves when the request is complete.
 */
export const saveUserContext = async (userContextList, callback = null) => {
    try {
        const response = await fetch(`${API_BASE_URL}/usercontext`, {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
            },
            body: userContextList, // Directly send the structured response
        });

        if (callback) {
            return callback(response);
        }

    } catch (error) {
        console.error('Error sending responses to /usercontext:', error);
        throw error;
    }
};

/**
 * Fetches the user context from the server based on the provided user and thread ID.
 * @returns {Promise<Object>} A promise that resolves to the user context data.
 */
export const fetchUserContext = () => {
    try {
        const url = new URL(`${API_BASE_URL}/usercontext`);
        return fetch(url.toString(), {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
            },
        })
    } catch (error) {
        console.error('Error fetching user context:', error);
        throw error;
    }
};

/**
 * Process a chunk of data, adding it to a buffer and extracting complete JSON objects.
 *
 * @param {string} chunk - The chunk of data to process.
 * @param {Object} buffer - The buffer object that stores the accumulated data.
 * @param {Object[]} userContextList - The list of UserContext objects to update with the extracted JSON objects.
 * @returns {Promise<void>} - A promise that resolves when the processing is complete.
 *
 * @throws {Error} - If there is an error parsing a JSON chunk.
 *
 * @example
 * // Usage example
 * const chunk = '{"id": "1", "model": "example", "completion": 0.75}';
 * const buffer = { value: '' };
 * const userContextList = { value: [] };
 *
 * processChunk(chunk, buffer, userContextList).catch(error => {
 *   console.error('Error processing chunk:', error);
 * });
 */
export const processChunk = async (chunk, buffer, userContextList) => {
    buffer.value += chunk;
    let boundary;

    while ((boundary = buffer.value.indexOf('}\n' + '{')) !== -1) {  // Find boundary between JSON objects
        const jsonString = buffer.value.slice(0, boundary + 1);
        buffer.value = buffer.value.slice(boundary + 1);

        let responseModel;
        try {
            responseModel = JSON.parse(jsonString);


            // Find the correct UserContext in the list
            const userContextIndex = userContextList.value.findIndex(
                uc => uc?.prompt?.uuid === responseModel.id
            );

            if (userContextIndex !== -1) {
                // Find the context_data entry for this model and id
                let contextDataIndex = userContextList.value[userContextIndex].prompt.context_data.findIndex(
                    cd => cd.id === responseModel.id && cd.model === responseModel.model
                );

                if (contextDataIndex === -1) {
                    // If not found, create a new entry
                    userContextList.value[userContextIndex].prompt.context_data.push(responseModel);
                } else {
                    // If found, update the existing entry
                    userContextList.value[userContextIndex].prompt.context_data[contextDataIndex].completion = responseModel.completion;
                }
            } else {
                console.error("UserContext not found for id:", responseModel.id);
            }
        } catch (error) {
            console.error("Error parsing JSON chunk:", error, jsonString);
        }
    }
};


/**
 * Represents a tag used in a tool call.
 *
 * The TOOL_CALL_TAG constant represents a specific string value, '<tool_call>', which can be used as a tag
 * within a tool call. This tag can be used to identify specific parts of the tool call or to differentiate
 * it from other types of tags.
 *
 * @constant {string} TOOL_CALL_TAG - The value of the tool call tag.
 */
const TOOL_CALL_TAG = 'tool_call*';
/**
 * The TOOL_CALL_END_TAG represents the end tag used to delimit the completion of a tool call.
 *
 * @constant {string} TOOL_CALL_END_TAG - The end tag string '</tool_call>'.
 */
const TOOL_CALL_END_TAG = '*tool_call';
/**
 * Specifies the length of the content in the TOOL_CALL_TAG.
 *
 * The TOOL_CALL_CONTENT_LENGTH variable represents the length of the content within the TOOL_CALL_TAG.
 * It is derived from the length of the TOOL_CALL_TAG.
 *
 * @type {number}
 * @readonly
 */
const TOOL_CALL_CONTENT_LENGTH = TOOL_CALL_TAG.length;

/**
 * Extracts the tool call string from the given content.
 *
 * @param {string} content - The content to extract the tool call string from.
 * @returns {string|null} - The extracted tool call string, or null if it cannot be found.
 */
const extractToolCallString = (content) => {
    const toolCallStart = content.indexOf(TOOL_CALL_TAG);
    const toolCallEnd = content.indexOf(TOOL_CALL_END_TAG);
    if (toolCallStart === -1 || toolCallEnd === -1) return null;

    const toolCallString = content.slice(toolCallStart + TOOL_CALL_CONTENT_LENGTH, toolCallEnd).trim();
    return toolCallString.replace(/[\n\r]/g, '');
};

/**
 * Extracts the tool call string from the content and executes the specified tool with the provided parameters.
 *
 * @async
 * @param {string} content - The content from which to extract the tool call string.
 * @returns {void} - Returns nothing.
 *
 * @throws {Error} - Throws an error if there is an issue processing the tool call.
 */
export const callTool = async (content) => {
    try {
        const cleanedToolCallString = extractToolCallString(content);
        if (!cleanedToolCallString) return;

        const toolCall = JSON.parse(cleanedToolCallString);
        if (toolCall?.tool_call) {
            const { tool, parameters } = toolCall.tool_call;
            console.log(`Tool ${tool} executed successfully with parameters`, parameters);
            return await runActions(tool, parameters);

        }
    } catch (error) {
        console.error("Error processing tool_call:", error);
    }
};

/**
 * Sendet einen Tool-Call an den Server und führt die entsprechende Funktion aus.
 *
 * @param {string} tool - Der Name des Tools/Funktion, das/die aufgerufen werden soll.
 * @param {Object} parameters - Die Parameter, die an das Tool/Funktion übergeben werden.
 * @returns {Promise<Object>} - Die Antwort vom Server.
 */
export const runActions = async (tool, parameters) => {
    try {
        const requestBody = {
                tool: tool,
                parameters: parameters
            }


        const response = await fetch(`${API_BASE_URL}/tools/call`, {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody),
        });

        if (!response.ok) {
            throw new Error(`Failed to call tool: ${tool}, status: ${response.status}`);
        }


        return await response.json();
    } catch (error) {
        console.error('Error calling tool:', error);
        throw error;
    }
};


/**
 * Extrahiert den Tool-Call-Block aus dem Buffer
 * @param {string} buffer - Der Textpuffer, der die gestreamten Daten enthält.
 * @returns {object|null} - Gibt das Tool-Call-Objekt zurück, falls es gefunden wird, oder null.
 */
export const extractToolCall = (buffer) => {
    const toolCallStart = buffer.indexOf('<tool_call>');
    const toolCallEnd = buffer.indexOf('</tool_call>');

    if (toolCallStart !== -1 && toolCallEnd !== -1) {
        const toolCallString = buffer.slice(toolCallStart + 11, toolCallEnd);
        try {
            return JSON.parse(toolCallString);
        } catch (error) {
            console.error("Error parsing tool_call JSON:", error);
            return null;
        }
    }
    return null;
};




/**
 * Deletes a user context by thread ID.
 * @param {number} threadId - The ID of the thread.
 * @returns {Promise<void>} A promise that resolves when the user context is deleted.
 */
export const deleteUserContext = async (threadId) => {
    try {
        const response = await fetch(`${API_BASE_URL}/usercontext/${threadId}`, {
            method: 'DELETE',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            throw new Error(`Failed to delete user context. HTTP status: ${response.status}`);
        }

        console.log(`User context with thread ID ${threadId} deleted successfully.`);
    } catch (error) {
        console.error('Error deleting user context:', error);
        throw error;
    }
};

/**
 * Exports to excel
 * @param user
 * @param thread_id
 * @returns {Promise<Response>}
 */
export const exportUserContextToExel = async (user, thread_id) => {

    try {
        const response = await fetch(`${API_BASE_URL}/usercontext/export/excel?user=${user}&thread_id=${thread_id}`, {
            method: 'GET',
            credentials: 'include'
        });

        if (!response.ok) {
            throw new Error(`Failed to export: ${response.statusText}`);
        }

        // Get the response as a Blob (binary large object)
        const blob = await response.blob();

        // Create a link element to download the file
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'user_context_export.xlsx'); // Set the file name
        document.body.appendChild(link);
        link.click();

        // Clean up after the download
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
    } catch (error) {
        console.error('Error exporting to Excel:', error);
    }
}

/**
 * Fetches telegram accounts from the server.
 * @returns {Promise<Array>} A promise that resolves to an array of telegram accounts.
 */
export const getTelegramAccounts = async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/socialmedia/telegram/accounts`, {
            credentials: 'include',  // Added credentials here
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching telegram accounts:', error);
        throw error;
    }
};


/**
 * Fetches prompts from the server.
 * @returns {Promise<Array>} A promise that resolves to an array of telegram accounts.
 */
export const fetchPrompts = async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/prompts`, {
            credentials: 'include',
            method: 'GET',
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching telegram accounts:', error);
        throw error;
    }
};

/**
 * Deletes prompt
 *
 * @returns {Promise<Array>} A promise that resolves to an array of telegram accounts.
 */
export const deletePromptById = async (id) => {
    try {
        const response = await fetch(`${API_BASE_URL}/prompts/${id}`, {
            credentials: 'include',
            method: 'DELETE',
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching telegram accounts:', error);
        throw error;
    }
};

/**
 * Fetches telegram accounts from the server.
 * @returns {Promise<Array>} A promise that resolves to an array of telegram accounts.
 */
export const sendSocialMediaMessage = async (provider, socialMediaMessage) => {
    try {
        const response = await fetch(`${API_BASE_URL}/socialmedia/${provider}/message/send`, {
            method: 'POST',
            credentials: 'include',  // Added credentials here
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(socialMediaMessage),
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error sending message:', error);
        throw error;
    }
};


/**
 * Generates an image based on the given prompt and parameters.
 * @param {Object} params - The parameters for image generation.
 * @param {string} params.prompt - The prompt for image generation.
 * @param {number} params.n - Number of images to generate.
 * @param {string} params.size - Size of the image to generate.
 * @param {string} params.quality - Quality of the image to generate.
 * @param {string} params.style - Style of the image to generate.
 * @returns {Promise<Object>} A promise that resolves to the generated image data.
 */
export const generateImage = async (params) => {
    const response = await fetch(`${API_BASE_URL}/generate/image`, {
        method: 'POST',
        credentials: 'include',  // Added credentials here
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(params),
    });

    return await response.json();
};

export const sendSocialMediaImageMessage = async (provider, messageData) => {
    const url = `${API_BASE_URL}/socialmedia/${provider}/image/send`;
    const response = await fetch(url, {
        method: 'POST',
        credentials: 'include',  // Added credentials here
        headers: {
            'Content-Type': 'application/json' // Ensure the server knows you're sending JSON
        },
        body: JSON.stringify(messageData), // Send the JSON data
    });

    // Return the JSON response
    return await response.json();
};


/**
 * Sends a POST request to the /gripsbox endpoint.
 * @param {Object} gripsboxData - The data to send to the gripsbox endpoint.
 * @returns {Promise<Object>} A promise that resolves to the server's response.
 */
export const postToGripsbox = async (formData) => {
    try {
        const response = await fetch(`${API_BASE_URL}/gripsbox`, {
            method: 'POST',
            credentials: 'include',  // Added credentials here
            body: formData,
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Error in postToGripsbox:', error);
        throw error;
    }
};

/**
 * Performs email/password login.
 * @param {string} email - The user's email.
 * @param {string} password - The user's password.
 * @returns {Promise<Object>} A promise that resolves to the login response data.
 */
export const loginWithEmailPassword = async (email, password) => {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            mode: 'no-cors',
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({email, password}),
        });

        if (!response.ok) {
            throw new Error('Login failed');
        }

        return await response.json();
    } catch (error) {
        console.error('Login error:', error);
        throw error;
    }
};

/**
 * Initiates Google OAuth login.
 * @returns {Promise<Object>} A promise that resolves to the Google OAuth initiation response.
 */
export const initiateGoogleAuth = async () => {
    try {
        window.location.href = `${API_BASE_URL}/auth/login/google`
    } catch (error) {
        console.error('Google auth initiation error:', error);
        throw error;
    }
};

export const fetchAccessToken = async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/session-info`, {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Error checking authentication:', error);
        return false;
    }
};


/**
 * Logs the user out by calling the /auth/logout endpoint.
 * @returns {Promise<void>}
 */
export const logout = async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/logout`, {
            method: 'GET',
            credentials: 'include', // Ensure the session cookie is sent
        });

        if (!response.ok) {
            throw new Error('Logout failed');
        }

        console.log('Logout successful');
    } catch (error) {
        console.error('Error during logout:', error);
        throw error;
    }
};
