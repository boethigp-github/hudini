const API_BASE_URL = import.meta.env.SERVER_URL || 'http://localhost:8000';

/**
 * Sends a prompt to the server and streams the response.
 * @param {Object} promptData - The data to send to the server.
 * @param {Function} onChunk - Callback function to handle each chunk of the response.
 * @param {Function} onError - Callback function to handle any errors.
 * @param {Function} onComplete - Callback function called when the stream is complete.
 */
export const streamPrompt = async (promptData, onChunk, onError, onComplete) => {
    try {
        const response = await fetch(`${API_BASE_URL}/stream`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(promptData),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const { done, value } = await reader.read();
            if (done) {
                onComplete();
                break;
            }
            const chunk = decoder.decode(value);
            onChunk(chunk);
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
 * @param {Object} promptData - The prompt data to save.
 * @returns {Promise<Object>} A promise that resolves to the server's response.
 */
export const createPrompt = async (promptData) => {
    try {
        const response = await fetch(`${API_BASE_URL}/prompt`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(promptData),
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
 * @param {object} structuredResponse - Array of response objects to send.
 * @returns {Promise<void>} A promise that resolves when the request is complete.
 */
export const sendResponsesToUserContext = async (structuredResponse) => {
    try {
        const response = await fetch(`${API_BASE_URL}/usercontext`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(structuredResponse), // Directly send the structured response
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
    } catch (error) {
        console.error('Error sending responses to /usercontext:', error);
        throw error;
    }
};