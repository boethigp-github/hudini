<!--suppress CheckImageSize -->
<template>
    <div class="chat-container">
        <div class="header">
            <img src="../assets/hidini2.webp" alt="Hudini Logo" class="logo" height="120" />
            <div class="title-container">
                <h1 class="title">{{ t('hudini_title') }}</h1>
                <div class="language-switch-container">
                    <LanguageSwitch />
                </div>
            </div>
        </div>
        <div class="content">
            <div class="chat-area">
                <ResponsePanel
                    ref="responsePanel"
                    :responses="responses"
                    :currentResponse="currentResponse"
                />
                <a-form layout="vertical" class="form">
                    <ModelSelection
                        :modelValue="modelsStore.selectedModels"
                        @update:modelValue="modelsStore.setSelectedModels"
                        :localModels="localModels"
                        :openaiModels="openaiModels"
                    />
                    <a-form-item class="textarea-container">
                        <a-textarea
                            v-model:value="prompt"
                            :rows="6"
                            :placeholder="t('enter_prompt')"
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
                            {{ t('send_button') }}
                        </a-button>
                    </a-form-item>
                </a-form>
            </div>
            <div class="previous-prompts">
                <h2>{{ t('previous_prompts') }}</h2>
                <PromptPanel :key="updateTrigger" />
            </div>
        </div>
    </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useModelsStore } from './../stores/models';
import PromptPanel from './PromptPanel.vue';
import ResponsePanel from './ResponsePanel.vue';
import LanguageSwitch from './LanguageSwitch.vue';
import ModelSelection from './ModelSelection.vue';
import { message } from 'ant-design-vue';
import { streamPrompt, getModels, savePrompt } from './../services/api';

export default {
    name: 'ChatForm',
    components: {
        PromptPanel,
        ResponsePanel,
        LanguageSwitch,
        ModelSelection,
    },
    setup() {
        const { t } = useI18n();

        const prompt = ref('');
        const responses = ref([]);
        const currentResponse = ref('');
        const loading = ref(false);
        const modelsStore = useModelsStore(); // Access the Pinia store
        const localModels = ref([]);
        const openaiModels = ref([]);
        const updateTrigger = ref(0);

        const savePromptToServer = async () => {
            if (!prompt.value || typeof prompt.value !== 'string' || prompt.value.trim() === '') {
                message.error(t('invalid_prompt'));
                return;
            }

            const promptData = {
                prompt: prompt.value.trim(),
                models: modelsStore.selectedModels,
            };

            try {
                await savePrompt(promptData);
                message.success(t('prompt_saved'));
                updateTrigger.value++;
            } catch (error) {
                message.error(t('failed_to_save_prompt'));
            }
        };

        const loadModels = async () => {
            try {
                const data = await getModels();
                localModels.value = data.local_models;
                openaiModels.value = data.openai_models;
                if (localModels.value.length > 0 && modelsStore.selectedModels.length === 0) {
                    modelsStore.setSelectedModels([localModels.value[0]]);
                } else if (openaiModels.value.length > 0 && modelsStore.selectedModels.length === 0) {
                    modelsStore.setSelectedModels([openaiModels.value[0]]);
                }
            } catch (error) {
                message.error(t('failed_to_load_models'));
            }
        };

        const handleKeydown = (event) => {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                handleSubmit();
            }
        };

        const handleSubmit = async () => {
            if (!prompt.value.trim() || modelsStore.selectedModels.length === 0) {
                message.error(t('enter_prompt_and_select_model'));
                return;
            }

            loading.value = true;
            currentResponse.value = '';

            const promptData = {
                prompt: prompt.value.trim(),
                models: modelsStore.selectedModels,
            };

            await streamPrompt(
                promptData,
                (chunk) => {
                    let parsedChunk;
                    try {
                        parsedChunk = JSON.parse(chunk);
                    } catch (error) {
                        console.error("Error parsing JSON chunk:", error);
                        return;
                    }

                    // Handle the status of the chunk
                    if (parsedChunk.status === "end") {
                        responses.value.push(currentResponse.value.trim());
                        currentResponse.value = '';
                    } else if (parsedChunk.status === "data") {
                        currentResponse.value += " "+parsedChunk.token;
                    } else if (parsedChunk.status === "error") {
                        currentResponse.value = `Error: ${parsedChunk.error}`;
                    }
                },
                (error) => {
                    console.error('Stream error:', error);
                    currentResponse.value = t('server_connection_error');
                    loading.value = false;
                },
                () => {
                    loading.value = false;
                    savePromptToServer();
                }
            );
        };




        onMounted(() => {
            loadModels();
            modelsStore.loadFromStorage(); // Load selected models from storage when the component mounts
        });

        return {
            prompt,
            responses,
            currentResponse,
            loading,
            modelsStore, // Expose the store to the template
            localModels,
            openaiModels,
            handleKeydown,
            handleSubmit,
            updateTrigger,
            t,
        };
    },
};
</script>

<style scoped>

.header {
    display: flex;
    align-items: center;
    padding: 1rem;
    background-color: #f0f2f5;
}


.title {
    font-size: 2.0rem;
    font-weight: bold;
    margin-bottom: 0.5rem;
}

</style>
