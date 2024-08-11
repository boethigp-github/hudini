<template>
    <div class="chat-container">
        <div class="header">
        <img src="./../assets/hidini2.webp" alt="Hudini Logo" class="logo" height="120" />
        <h1 class="title">Hudini - CPU Magican on SLM</h1>
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
        const prompt = ref('');
        const response = ref('');
        const loading = ref(false);
        const responseRef = ref(null);
        const previousPrompts = ref([]);

        const loadPrompts = async () => {
            try {
                const res = await fetch('http://localhost:5000/load_prompts');
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
            if (!prompt.value.trim()) {
                return;
            }

            loading.value = true;
            response.value = '';

            try {
                const res = await fetch('http://localhost:5000/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: prompt.value }),
                });

                if (!res.ok) throw new Error('Network response was not ok');

                const eventSource = new EventSource('http://localhost:5000/stream');
                eventSource.onmessage = (event) => {
                    console.log('Event data:', event.data);
                    if (event.data === '[END]') {
                        eventSource.close();
                        loading.value = false;
                        savePrompt(); // Save prompt after successful generation
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
                // Check for exact match locally
                const isDuplicate = previousPrompts.value.some(p => p.prompt.trim().toLowerCase() === prompt.value.trim().toLowerCase());

                if (isDuplicate) {
                    console.log('Duplicate prompt detected, aborting silently');
                    return;
                }

                const res = await fetch('http://localhost:5000/save_prompt', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: prompt.value }),
                });

                if (res.ok) {
                    await loadPrompts(); // Reload prompts after saving
                }
            } catch (error) {
                console.error('Error saving prompt:', error);
            }
        };

        const deletePrompt = async (id) => {
            try {
                const res = await fetch(`http://localhost:5000/delete_prompt/${id}`, {
                    method: 'DELETE',
                    headers: { 'Content-Type': 'application/json' },
                });

                if (res.ok) {
                    await loadPrompts(); // Reload prompts after deletion
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
            return date.toLocaleString(); // You can customize this format as needed
        };

        watch(response, scrollToBottom);

        onMounted(loadPrompts);

        return {
            prompt,
            response,
            loading,
            responseRef,
            previousPrompts,
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
@import './../assets/chat-styles.css';
</style>
