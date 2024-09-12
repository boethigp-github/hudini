import {UserContext} from "@/vue/models/UserContext.js";

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
        const response = await fetch(`${API_BASE_URL}/models`);
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
 * @param {string} user - The UUID of the user.
 * @param {number} threadId - The ID of the thread.
 * @returns {Promise<Object>} A promise that resolves to the user context data.
 */
export const fetchUserContext = (user, threadId) => {
    try {


        const url = new URL(`${API_BASE_URL}/usercontext`);
        url.searchParams.append('user', user);
        url.searchParams.append('thread_id', String(threadId));

        return fetch(url.toString(), {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        })
    } catch (error) {
        console.error('Error fetching user context:', error);
        throw error;
    }
};

const cloneUserContext = (userContext) => {
    const userContextPostRequestModel = new UserContext.UserContextPostRequestModel()
    userContextPostRequestModel.uuid = userContext.value.uuid
    userContextPostRequestModel.prompt = userContext.value.prompt
    userContextPostRequestModel.thread_id = userContext.value.thread_id
    userContextPostRequestModel.user = userContext.value.user
    return userContextPostRequestModel
}


export const processChunk = (chunk, buffer, userContext, userContextList) => {
    buffer.value += chunk; // Add chunk to buffer
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
 * Deletes a user context by thread ID.
 * @param {number} threadId - The ID of the thread.
 * @returns {Promise<void>} A promise that resolves when the user context is deleted.
 */
export const deleteUserContext = async (threadId) => {
    try {
        const response = await fetch(`${API_BASE_URL}/usercontext/${threadId}`, {
            method: 'DELETE',
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
        const response = await fetch(`${API_BASE_URL}/socialmedia/telegram/accounts`);
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
             headers: {
                'Content-Type': 'application/json' // Ensure the server knows you're sending JSON
            },
            body: JSON.stringify(messageData) // Send the FormData object directly
        });

        // Return the JSON response
        return await response.json();
};
