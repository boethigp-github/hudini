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
                    <ModelSelection />
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
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useModelsStore } from './../stores/models';
import PromptPanel from './PromptPanel.vue';
import ResponsePanel from './ResponsePanel.vue';
import LanguageSwitch from './LanguageSwitch.vue';
import ModelSelection from './ModelSelection.vue';
import { message } from 'ant-design-vue';
import { streamPrompt, savePrompt } from './../services/api';

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
        const currentResponse = ref(null); // Modified to hold an object instead of a string
        const loading = ref(false);
        const modelsStore = useModelsStore();
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
            currentResponse.value = null; // Reset the currentResponse object

            const promptData = {
                prompt: prompt.value.trim(),
                models: modelsStore.selectedModels,
            };

            const responseIndexMap = new Map();

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

                    const promptId = parsedChunk.prompt_id;

                    if (parsedChunk.status === "data") {
                        if (responseIndexMap.has(promptId)) {
                            // Update the current response object
                            const index = responseIndexMap.get(promptId);
                            responses.value[index].token += " " + parsedChunk.token;
                            currentResponse.value.token += " " + parsedChunk.token; // Update the token in currentResponse
                        } else {
                            // Initialize the response object if it doesn't exist
                            const newResponse = {
                                status: "data",
                                token: parsedChunk.token,
                                data: parsedChunk.data,
                                timestamp: parsedChunk.timestamp,
                                user: parsedChunk.user,
                                prompt: parsedChunk.prompt,
                                prompt_id: parsedChunk.prompt_id,
                                model: parsedChunk.model,
                            };
                            responseIndexMap.set(promptId, responses.value.length);
                            responses.value.push(newResponse);
                            currentResponse.value = { ...newResponse }; // Set currentResponse to this new response
                        }
                    } else if (parsedChunk.status === "end") {
                        // Finalize the response for this prompt_id
                        if (responseIndexMap.has(promptId)) {
                            const index = responseIndexMap.get(promptId);
                            responses.value[index].status = "complete";
                        }
                        currentResponse.value = null; // Clear the currentResponse object
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

        return {
            prompt,
            responses,
            currentResponse,
            loading,
            modelsStore,
            handleKeydown,
            handleSubmit,
            updateTrigger,
            t,
        };
    },
};
</script>

<style scoped>


.title {
    font-size: 2.0rem;
    font-weight: bold;
    margin-bottom: 0.5rem;
}

</style>
