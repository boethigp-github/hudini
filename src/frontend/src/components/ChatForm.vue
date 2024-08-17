<template>
    <div class="chat-container">
        <div class="header">
            <!--suppress CheckImageSize -->
            <img src="../assets/hidini2.webp" alt="Hudini Logo" class="logo" height="120" />
            <div class="title-container">
                <h1 class="title">{{ $t('hudini_title') }}</h1>
                <div class="language-switch-container">
                    <LanguageSwitch />
                </div>
            </div>
        </div>
        <div class="content">
            <div class="chat-area">
                <!-- Pass the 'responses' and 'currentResponse' props to the ResponsePanel component -->
                <ResponsePanel
                    ref="responsePanel"
                    :responses="responses"
                    :currentResponse="currentResponse"
                />
                <a-form layout="vertical" class="form">
                    <a-form-item :label="$t('select_model')">
                        <a-select v-model:value="selectedModel">
                            <a-select-opt-group label="Local Models">
                                <a-select-option v-for="model in localModels" :key="model" :value="model">
                                    {{ model }}
                                </a-select-option>
                            </a-select-opt-group>
                            <a-select-opt-group label="OpenAI Models">
                                <a-select-option v-for="model in openaiModels" :key="model" :value="model">
                                    {{ model }}
                                </a-select-option>
                            </a-select-opt-group>
                        </a-select>
                    </a-form-item>
                    <a-form-item class="textarea-container">
                        <a-textarea
                            v-model:value="prompt"
                            :rows="6"
                            :placeholder="$t('enter_prompt')"
                            @keydown="handleKeydown"
                            class="prompt_input"
                            :disabled="loading"
                        />
                        <a-button
                            type="primary"
                            @click="handleSubmit"
                            :loading="loading"
                            class="send-button"
                        >
                            {{ $t('send_button') }}
                        </a-button>
                    </a-form-item>
                </a-form>
            </div>
            <div class="previous-prompts">
                <h2>{{ $t('previous_prompts') }}</h2>
                <PromptPanel :key="updateTrigger" />
            </div>
        </div>
    </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import PromptPanel from './PromptPanel.vue';
import ResponsePanel from './ResponsePanel.vue';
import LanguageSwitch from './LanguageSwitch.vue'; // Import the LanguageSwitch component
import { message } from 'ant-design-vue'; // Add this import statement

export default {
    name: 'ChatForm',
    components: {
        PromptPanel,
        ResponsePanel,
        LanguageSwitch, // Register the LanguageSwitch component
    },
    setup() {
        const serverUrl = import.meta.env.VITE_SERVER_URL || 'http://localhost:5000';
        const prompt = ref('');
        const responses = ref([]); // Store all responses
        const currentResponse = ref(''); // Store current streaming response
        const loading = ref(false);
        const selectedModel = ref('');
        const localModels = ref([]);
        const openaiModels = ref([]);
        const updateTrigger = ref(0);

        const savePrompt = () => {
            if (!prompt.value || typeof prompt.value !== 'string' || prompt.value.trim() === '') {
                message.error(t('invalid_prompt'));
                return;
            }

            const rawPrompt = prompt.value.trim();

            fetch(`${serverUrl}/save_prompt`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ prompt: rawPrompt }),
            })
                .then(res => {
                    if (!res.ok) {
                        throw new Error("Failed to save prompt");
                    }
                    message.success('Prompt saved successfully');
                    updateTrigger.value++;
                })
                .catch(error => {
                    console.error("Error saving prompt", error);
                    message.error(t('failed_to_save_prompt'));
                });
        };

        const loadModels = () => {
            fetch(`${serverUrl}/get_models`)
                .then(res => {
                    if (!res.ok) throw new Error("Failed to load models");
                    return res.json();
                })
                .then(data => {
                    localModels.value = data.local_models;
                    openaiModels.value = data.openai_models;
                    if (localModels.value.length > 0) {
                        selectedModel.value = localModels.value[0];
                    } else if (openaiModels.value.length > 0) {
                        selectedModel.value = openaiModels.value[0];
                    }
                })
                .catch(error => {
                    console.error("Error loading models:", error);
                });
        };

        const handleKeydown = (event) => {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                handleSubmit();
            }
        };

        const handleSubmit = () => {
            if (!prompt.value.trim() || !selectedModel.value) {
                message.error('Please enter a prompt and select a model.');
                return;
            }

            // Log the data being sent to the server
            console.log('Prompt:', prompt.value.trim());
            console.log('Selected Model:', selectedModel.value);

            // Save the prompt
            savePrompt();

            loading.value = true;

            // Create the payload for the /stream request
            const requestPayload = {
                prompt: prompt.value.trim(),
                model: selectedModel.value
            };

            // Log the payload
            console.log('Sending data to /stream endpoint:', requestPayload);

            // Send prompt and model to the server
            const eventSource = new EventSource(`${serverUrl}/stream?prompt=${encodeURIComponent(requestPayload.prompt)}&model=${encodeURIComponent(requestPayload.model)}`);
            eventSource.onmessage = (event) => {
                if (event.data === '[END]') {
                    // Add the current response to the list of responses
                    responses.value.push(currentResponse.value.trim());
                    currentResponse.value = ''; // Clear the current response
                    eventSource.close();
                    loading.value = false;
                } else if (event.data.startsWith('[ERROR]')) {
                    currentResponse.value = event.data.substring(8); // Remove '[ERROR]' prefix
                    eventSource.close();
                    loading.value = false;
                } else {
                    currentResponse.value += event.data + ' ';
                }
            };

            eventSource.onerror = (error) => {
                console.error('EventSource failed:', error);
                currentResponse.value = 'An error occurred while connecting to the server.';
                eventSource.close();
                loading.value = false;
            };
        };

        onMounted(() => {
            loadModels();
        });

        return {
            prompt,
            responses,
            currentResponse,
            loading,
            selectedModel,
            localModels,
            openaiModels,
            handleKeydown,
            handleSubmit,
            updateTrigger,
        };
    },
};
</script>

<style scoped>
.title {
    font-size: 2.5rem; /* Adjust size as needed */
    font-weight: bold;
    margin-bottom: 10px; /* Space between title and language switch */
    text-align: left;
    /* Ensure the title is always at the top left */
}
</style>
