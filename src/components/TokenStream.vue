<!--suppress ExceptionCaughtLocallyJS -->
<template>
    <div class="chat-container">
        <div class="header">
            <!--suppress CheckImageSize -->
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
                            :placeholder="$t('enter_prompt')"
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
                            {{ $t('send_button') }}
                        </a-button>
                    </a-form-item>
                </a-form>
            </div>
            <div class="previous-prompts">
                <PromptPanel/>
            </div>
        </div>
    </div>
</template>

<script>
import { ref, watch, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import PromptPanel from './PromptPanel.vue';

export default {
    components: {
        PromptPanel
    },
    setup() {
        const { locale } = useI18n();
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
        });

        const formatTimestamp = (timestamp) => {
            const date = new Date(timestamp);
            return date.toLocaleString();
        };


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
            changeLanguage,
            selectedLanguage,
            formatTimestamp
        };
    },
};
</script>
