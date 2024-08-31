<template>
  <a-form layout="vertical" class="form">
    <a-form-item class="textarea-container">
      <div class="prompt-input-wrapper">
        <a-textarea
          spellcheck="false"
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
      </div>
    </a-form-item>
  </a-form>
</template>

<script>
import { ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { useModelsStore } from './../../stores/models';
import { message } from 'ant-design-vue';
import { streamPrompt, createPrompt } from './../../services/api';
import { v4 as uuidv4 } from 'uuid';

export default {
  name: 'PromptForm',
  setup() {
    const { t } = useI18n();
    const prompt = ref('');
    const loading = ref(false);
    const modelsStore = useModelsStore();
    const buffer = ref(''); // Buffer to hold incomplete JSON strings

    const createPromptServerside = async (prompt_id) => {
      if (!prompt.value || typeof prompt.value !== 'string' || prompt.value.trim() === '') {
        message.error(t('invalid_prompt'));
        return;
      }

      const promptData = {
        prompt: prompt.value.trim(),
        user: 'anonymous',
        status: 'prompt-saved',
        id: prompt_id,
      };

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

    const processChunk = (chunk) => {
      buffer.value += chunk; // Add chunk to buffer

      let boundary;
      while ((boundary = buffer.value.indexOf('}{')) !== -1) {
        const jsonString = buffer.value.slice(0, boundary + 1);
        buffer.value = buffer.value.slice(boundary + 1);

        let responseModel;
        try {
          responseModel = JSON.parse(jsonString);
          // Process the response model further if needed
        } catch (error) {
          console.log('Error parsing JSON chunk:', error, jsonString);
        }
      }
    };

    const handleSubmit = async () => {
      if (!prompt.value.trim() || modelsStore.selectedModels.length === 0) {
        message.error(t('enter_prompt_and_select_model'));
        return;
      }

      loading.value = true;

      const prompt_id = uuidv4();

      await createPromptServerside(prompt_id);

      const serviceResponse = await modelsStore.getServiceResponse();

      if (!serviceResponse) {
        message.error(t('failed_to_retrieve_model_information'));
        loading.value = false;
        return;
      }

      const selectedModelInfo = modelsStore.selectedModels.map((modelId) => {
        const fullModelInfo = serviceResponse.find((model) => model.id === modelId);
        return fullModelInfo || { id: modelId, platform: 'unknown' };
      });

      const promptData = {
        prompt_id: prompt_id,
        prompt: prompt.value.trim(),
        models: selectedModelInfo,
      };

      await streamPrompt(
        promptData,
        processChunk,
        (error) => {
          console.error('Stream error:', error);
          loading.value = false;
        },
        () => {
          loading.value = false;
        }
      );
    };

    // Watch for changes in loading, and clear the prompt when loading is set to false
    watch(loading, (newValue) => {
      if (!newValue) {
        prompt.value = '';
      }
    });

    return {
      prompt,
      loading,
      handleKeydown,
      handleSubmit,
      t,
    };
  },
};
</script>

<style scoped>
.prompt-input-wrapper {
  position: relative;
  display: flex;
  align-items: flex-start;
}

.prompt_input {
  margin-top: 2px;
  padding-right: 100px; /* Make space for the button */
  width: 100%;
  padding-bottom: 5px;
  overflow: hidden;
  font-size: 14px;
  font-family: 'Georgia', Tahoma, Geneva, Verdana, sans-serif;
  border: none;
  color: #292929;
  font-weight: bold;
}

.send-button,
.send-button:hover {
  position: absolute;
  right: 10px;
  top: 12px; /* Adjust this value to vertically align the button as desired */
  background: darkgrey;
}

.send-button:hover {
  background: #1f2611;
}

.textarea-container {
  clear: both;
}
</style>
