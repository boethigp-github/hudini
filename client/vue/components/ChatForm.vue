<!--suppress CheckImageSize -->
<template>
  <div class="chat-container">
    <div class="header">
      <img src="../assets/hidini2.webp" alt="Hudini Logo" class="logo" height="60" />
      <div class="language-switch-container">
        <LanguageSwitch />
      </div>
    </div>
    <div class="content">
      <div class="chat-area">
        <ResponsePanel
            :responses="responses"
            :loading="loading"
        />
        <a-form layout="vertical" class="form">
          <ModelSelection />

          <a-form-item class="textarea-container">
            <a-textarea
                v-model:value="prompt"
                :rows="2"
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
import { streamPrompt, createPrompt } from './../services/api';
import { v4 as uuidv4 } from 'uuid';

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
    const loading = ref(false);
    const modelsStore = useModelsStore();
    const updateTrigger = ref(0);
    const storedPrompt = ref({status:'initialized', prompt:null, prompt_id:null});

    const createPromptServerside = async () => {
      if (!prompt.value || typeof prompt.value !== 'string' || prompt.value.trim() === '') {
        message.error(t('invalid_prompt'));
        return;
      }

      const promptData = {
        prompt: prompt.value.trim(),
        user: 'anonymous',
        status: 'prompt-saved',
        id: uuidv4(),
      };
      responses.value.push(promptData)

      updateTrigger.value++;
      try {
        await createPrompt(promptData);
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

      createPromptServerside();


      const promptData = {
        prompt: prompt.value.trim(),
        models: modelsStore.selectedModels,
      };

      await streamPrompt(
          promptData,
          (completion) => {
            let parsedCompletion;
            try {
              parsedCompletion = JSON.parse(completion);
              console.log("parsedCompletion", parsedCompletion);
            } catch (error) {
              console.error("Error parsing JSON chunk:", error);
              return;
            }

            responses.value.push({ ...parsedCompletion, status: 'complete' });
          },
          (error) => {
            console.error('Stream error:', error);
            responses.value.push({
              status: 'error',
              token: t('server_connection_error'),
            });
            loading.value = false;
          },
          () => {
            loading.value = false;
          }
      );
    };

    return {
      prompt,
      responses,
      loading,
      modelsStore,
      storedPrompt,
      handleKeydown,
      handleSubmit,
      updateTrigger,
      t,
    };
  },
};
</script>

<style scoped>

.prompt_input{
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  color: #444444;
  margin-top: 10px;
}

.textarea-container{
  clear: both;
}

.language-switch-container{
  width: 100%;
}


.chat-area{

  width: 100%;
  max-width: 100%;
}
</style>