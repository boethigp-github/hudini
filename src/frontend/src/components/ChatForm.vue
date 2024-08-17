<!--suppress ExceptionCaughtLocallyJS, CheckImageSize -->
<template>
    <div class="chat-container">
        <div class="header">
            <img src="../assets/hidini2.webp" alt="Hudini Logo" class="logo" height="120" />
            <h1 class="title">{{ $t('hudini_title') }}</h1>
            <a-select v-model:value="selectedLanguage" @change="changeLanguage" style="width: 120px; position: absolute; right: 20px; top: 20px;">
                <a-select-option value="en">English</a-select-option>
                <a-select-option value="de">Deutsch</a-select-option>
                <a-select-option value="fr">Français</a-select-option>
                <a-select-option value="ru">Русский</a-select-option>
                <a-select-option value="zh">中文</a-select-option>
            </a-select>
        </div>
        <div class="content">
            <div class="chat-area">
                <div id="response" class="response" ref="responseRef">
                    <div v-if="!response" class="placeholder">
                        {{ $t('your_response') }}
                    </div>
                    <div>{{ response }}</div>
                </div>
                <a-form layout="vertical" class="form">
                    <a-form-item :label="$t('select_model')">
                        <a-select v-model:value="selectedModel" class="">
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
                <p v-if="noPrompts">{{ $t('no_prompts') }}</p> <!-- Show message if no prompts -->
                <PromptPanel v-else/>
            </div>
        </div>
    </div>
</template>

<script>
import { ref, watch, onMounted, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { message } from 'ant-design-vue';
import PromptPanel from './PromptPanel.vue';

export default {
    components: {
        PromptPanel
    },
    setup() {
        const { t } = useI18n();
        const selectedLanguage = ref(localStorage.getItem('locale') || 'de');

        const changeLanguage = (value) => {
            locale.value = value;
            localStorage.setItem('locale', value);
        };

        const serverUrl = import.meta.env.VITE_SERVER_URL || 'http://localhost:5000';
        const prompt = ref('');
        const response = ref('');
        const loading = ref(false);
        const responseRef = ref(null);
        const previousPrompts = ref([]);
        const selectedModel = ref('');
        const localModels = ref([]);
        const openaiModels = ref([]);

        const loadPrompts = async () => {
            try {
                const res = await fetch(`${serverUrl}/load_prompts`);
                if (!res.ok) {
                    throw new Error("Failed to load prompts");
                }
                previousPrompts.value = await res.json();
            } catch (error) {
                console.error("Error loading prompts:", error);
                message.error(t('failed_to_load_prompts'));
            }
        };

        const noPrompts = computed(() => previousPrompts.value.length === 0); // Computed property to check if prompts are empty

        const savePrompt = async () => {
            try {
                const rawPrompt = prompt.value.trim();  // Get the raw string value
                const isDuplicate = previousPrompts.value.some(
                    (p) => p.prompt.trim().toLowerCase() === rawPrompt.toLowerCase()
                );

                if (isDuplicate) {
                    console.log("Duplicate prompt detected, aborting silently");
                    return;
                }

                const res = await fetch(`${serverUrl}/save_prompt`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ prompt: rawPrompt }),  // Send the raw value
                });

                if (res.ok) {
                    await loadPrompts();
                }
            } catch (error) {
                console.error("Error saving prompt", error);
                message.error(t('failed_to_save_prompt'));  // Show error message
            }
        };

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

            await savePrompt();  // Call savePrompt without passing the prompt explicitly

            loading.value = true;
            response.value = '';

            try {
                const res = await fetch(`${serverUrl}/generate`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: prompt.value.trim(), model: selectedModel.value }),  // Use prompt.value.trim()
                });

                if (!res.ok) throw new Error('Network response was not ok');

                const eventSource = new EventSource(`${serverUrl}/stream`);
                eventSource.onmessage = (event) => {
                    console.log('Event data:', event.data);
                    if (event.data === '[END]') {
                        eventSource.close();
                        loading.value = false;

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

        const scrollToBottom = () => {
            if (responseRef.value) {
                responseRef.value.scrollTop = responseRef.value.scrollHeight;
            }
        };

        watch(response, scrollToBottom);

        onMounted(() => {
            loadModels();
            loadPrompts();  // Load previous prompts on component mount
        });

        const formatTimestamp = (timestamp) => {
            const date = new Date(timestamp);
            return date.toLocaleString();
        };

        return {
            t,
            prompt,
            response,
            loading,
            responseRef,
            previousPrompts,
            noPrompts,  // Include the computed property in the return object
            selectedModel,
            localModels,
            openaiModels,
            handleKeydown,
            handleSubmit,
            changeLanguage,
            selectedLanguage,
            formatTimestamp
        };
    },
};
</script>
