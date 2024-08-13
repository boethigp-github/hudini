<template>
    <div class="chat-container">
        <div class="header">
            <img src="../assets/hidini2.webp" alt="Hudini Logo" class="logo" height="120" />
            <h1 class="title">Hudini - CPU Magician on SLM</h1>
        </div>
        <div class="content">
            <div class="chat-area">
                <div id="response" class="response" ref="responseRef">
                    <div v-if="!response" class="placeholder">
                        Your response will appear here
                    </div>
                    <div>{{ response }}</div>
                </div>
                <a-form layout="vertical" class="form">
                    <a-form-item label="Select Model">
                        <a-select v-model:value="selectedModel" style="width: 100%">
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
                            placeholder="Enter your prompt here..."
                            @keydown="handleKeydown"
                            class="textarea"
                            :disabled="loading"
                        />
                        <a-button
                            type="primary"
                            @click="handleSubmit"
                            :loading="loading"
                            class="send-button"
                        >
                            Send
                        </a-button>
                    </a-form-item>
                </a-form>
            </div>
            <div class="previous-prompts">
                <h2>Previous Prompts</h2>
                <ul>
                    <li v-for="item in previousPrompts" :key="item.id">
                        <div class="prompt-item">
                            <div class="timestamp">{{ formatTimestamp(item.timestamp) }}</div>
                            <span @click="loadPrompt(item.prompt)">{{ item.prompt }}</span>
                            <a-button type="link" @click="deletePrompt(item.id)" class="delete-button">
                                Delete
                            </a-button>
                        </div>
                    </li>
                </ul>
            </div>
        </div>
    </div>
</template>

<script>
import { ref, watch, onMounted } from 'vue';

export default {
    setup() {
        const serverUrl = import.meta.env.VITE_SERVER_URL || 'http://localhost:5000';
        const prompt = ref('');
        const response = ref('');
        const loading = ref(false);
        const responseRef = ref(null);
        const previousPrompts = ref([]);
        const selectedModel = ref('');
        const localModels = ref([]);
        const openaiModels = ref([]);

        const loadModels = async () => {
            try {
                const res = await fetch(`${serverUrl}/get_models`);
                if (!res.ok) throw new Error('Failed to load models');
                const data = await res.json();
                localModels.value = data.local_models;
                openaiModels.value = data.openai_models;
                if (localModels.value.length > 0) {
                    selectedModel.value = localModels.value[0];
                } else if (openaiModels.value.length > 0) {
                    selectedModel.value = openaiModels.value[0];
                }
            } catch (error) {
                console.error('Error loading models:', error);
            }
        };

        const loadPrompts = async () => {
            try {
                const res = await fetch(`${serverUrl}/load_prompts`);
                if (!res.ok) throw new Error('Failed to load prompts');
                previousPrompts.value = await res.json();
            } catch (error) {
                console.error('Error loading prompts:', error);
            }
        };

        const loadPrompt = (selectedPrompt) => {
            prompt.value = selectedPrompt;
        };

        const handleKeydown = (event) => {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                handleSubmit();
            }
        };

        const handleSubmit = async () => {
            if (!prompt.value.trim() || !selectedModel.value) {
                return;
            }

            loading.value = true;
            response.value = '';

            try {
                const res = await fetch(`${serverUrl}/generate`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: prompt.value, model: selectedModel.value }),
                });

                if (!res.ok) throw new Error('Network response was not ok');

                const eventSource = new EventSource(`${serverUrl}/stream`);
                eventSource.onmessage = (event) => {
                    console.log('Event data:', event.data);
                    if (event.data === '[END]') {
                        eventSource.close();
                        loading.value = false;
                        savePrompt();
                    } else if (event.data.startsWith('[ERROR]')) {
                        response.value = event.data;
                        eventSource.close();
                        loading.value = false;
                    } else {
                        response.value += event.data + ' ';
                        scrollToBottom();
                    }
                };
                eventSource.onerror = (error) => {
                    console.error('EventSource failed:', error);
                    eventSource.close();
                    loading.value = false;
                };
            } catch (error) {
                console.error('There was an error:', error);
                response.value = 'An error occurred while processing your request.';
                loading.value = false;
            }
        };

        const savePrompt = async () => {
            try {
                const isDuplicate = previousPrompts.value.some(p => p.prompt.trim().toLowerCase() === prompt.value.trim().toLowerCase());

                if (isDuplicate) {
                    console.log('Duplicate prompt detected, aborting silently');
                    return;
                }

                const res = await fetch(`${serverUrl}/save_prompt`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: prompt.value }),
                });

                if (res.ok) {
                    await loadPrompts();
                }
            } catch (error) {
                console.error('Error saving prompt:', error);
            }
        };

        const deletePrompt = async (id) => {
            try {
                const res = await fetch(`${serverUrl}/delete_prompt/${id}`, {
                    method: 'DELETE',
                });

                if (res.ok) {
                    await loadPrompts();
                }
            } catch (error) {
                console.error('Error deleting prompt:', error);
            }
        };

        const scrollToBottom = () => {
            if (responseRef.value) {
                responseRef.value.scrollTop = responseRef.value.scrollHeight;
            }
        };

        const formatTimestamp = (timestamp) => {
            const date = new Date(timestamp);
            return date.toLocaleString();
        };

        watch(response, scrollToBottom);

        onMounted(() => {
            loadModels();
            loadPrompts();
        });

        return {
            prompt,
            response,
            loading,
            responseRef,
            previousPrompts,
            selectedModel,
            localModels,
            openaiModels,
            handleKeydown,
            handleSubmit,
            loadPrompt,
            deletePrompt,
            formatTimestamp,
        };
    },
};
</script>

<style scoped>
@import '../assets/chat-styles.css';
</style>
