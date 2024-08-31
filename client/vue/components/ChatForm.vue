<template>
  <div class="chat-container">
    <div style="display: block;min-height: 10px;cursor: pointer" class="chat-header" >
      <div class="header">
        <img src="../assets/hidini2.webp" alt="Hudini Logo" class="logo" height="60"/>
        <ChatMenu/>
        <div class="language-switch-container">
          <LanguageSwitch/>
        </div>
      </div>
    </div>
    <div class="content">
      <div class="chat-area">
        <ResponsePanel
            :responses="responses"
            :loading="loading"/>
        <!-- Ant Design Vue Tabs -->
        <a-tabs default-active-key="1" class="chat-tabs" style="clear: both">
          <a-tab-pane key="1" :tab="t('model_selection')">
            <ModelSelection/>
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
                      class="send-button">
                    {{ t('send_button') }}
                  </a-button>
                </div>
              </a-form-item>
            </a-form>
          </a-tab-pane>
        </a-tabs>
      </div>
      <div class="previous-prompts">
        <h2>{{ t('previous_prompts') }}</h2>
        <PromptPanel :key="updateTrigger"/>
      </div>
    </div>
  </div>
</template>

<script>
import {ref, watch} from 'vue';
import {useI18n} from 'vue-i18n';
import {useModelsStore} from './../stores/models';
import PromptPanel from './PromptPanel.vue';
import ResponsePanel from './ResponsePanel.vue';
import LanguageSwitch from './LanguageSwitch.vue';
import ModelSelection from './ModelSelection.vue';
import {message} from 'ant-design-vue';
import {streamPrompt, createPrompt} from './../services/api';
import {v4 as uuidv4} from 'uuid';
import ChatMenu from './MainMenu.vue';
import {Tabs, TabPane} from 'ant-design-vue';
import {PlusOutlined, SettingOutlined} from '@ant-design/icons-vue';

export default {
  name: 'ChatForm',
  components: {
    PromptPanel,
    ResponsePanel,
    LanguageSwitch,
    ModelSelection,
    ChatMenu,
    Tabs,
    TabPane,
    PlusOutlined,
    SettingOutlined
  },
  setup() {
    const {t} = useI18n();
    const prompt = ref('');
    const responses = ref([]);
    const loading = ref(false);
    const isHeaderVisible = ref(false);
    const modelsStore = useModelsStore();
    const updateTrigger = ref(0);
    const buffer = ref(''); // Buffer to hold incomplete JSON strings

    const showDrawer = () => {
      drawerVisible.value = true;
    };

    const handleToolbarAction = ({key}) => {
      if (key === 'new_chat') {
        console.log("New Chat Started");
        // Implement new chat initiation logic
      } else if (key === 'settings') {
        console.log("Settings Opened");
        // Implement settings adjustment logic
      }
    };

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

    const processChunk = (chunk) => {
      buffer.value += chunk; // Add chunk to buffer

      let boundary;
      while ((boundary = buffer.value.indexOf('}{')) !== -1) {  // Find boundary between JSON objects
        const jsonString = buffer.value.slice(0, boundary + 1);
        buffer.value = buffer.value.slice(boundary + 1);

        let responseModel;
        try {
          responseModel = JSON.parse(jsonString);

          // Check if the response with the same prompt_id and model exists
          const responseIndex = responses.value.findIndex(
              r => r.prompt_id === responseModel.prompt_id && r.model === responseModel.model
          );

          if (responseIndex !== -1) {
            // Update existing response by replacing the entire object
            responses.value[responseIndex] = {
              ...responses.value[responseIndex],
              completion: responseModel.completion,
            };
          } else {
            // Add new response, ensuring no overwriting occurs
            responses.value.push(responseModel);
          }
        } catch (error) {
          console.log("Error parsing JSON chunk:", error, jsonString);
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

      const selectedModelInfo = modelsStore.selectedModels.map(modelId => {
        const fullModelInfo = serviceResponse.find(model => model.id === modelId);
        return fullModelInfo || {id: modelId, platform: 'unknown'};
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

    // Watch for changes in loading, and clear the prompt when loading is set to false
    watch(loading, (newValue) => {
      if (!newValue) {
        prompt.value = '';
      }
    });

    return {
      prompt,
      responses,
      loading,
      modelsStore,
      handleKeydown,
      handleSubmit,
      updateTrigger,
      showDrawer,
      handleToolbarAction,
      isHeaderVisible,
      t,
    };
  },
};
</script>

<style scoped>
.header {
  display: flex;
  align-items: center;
}

.header .logo {
  margin-right: 10px;
}

.language-switch-container {
  width: 100%;
}

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

.send-button, .send-button:hover {
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

.chat-area {
  width: 100%;
  max-width: 100%;
}
</style>