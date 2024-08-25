<template>
  <div class="chat-container">
    <div class="header">
      <img src="../assets/hidini2.webp" alt="Hudini Logo" class="logo" height="60" />
      <ChatMenu />
      <div class="language-switch-container">
        <LanguageSwitch />
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
            <ModelSelection />
            <a-form layout="vertical" class="form">
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
                    class="send-button">
                  {{ t('send_button') }}
                </a-button>
              </a-form-item>
            </a-form>
          </a-tab-pane>
        </a-tabs>
      </div>
      <div class="previous-prompts">
        <h2>{{ t('previous_prompts') }}</h2>
        <PromptPanel :key="updateTrigger" />
      </div>
    </div>
  </div>
</template>


<script>
import { ref, watch , onMounted, onBeforeUnmount} from 'vue';
import { useI18n } from 'vue-i18n';
import { useModelsStore } from './../stores/models';
import PromptPanel from './PromptPanel.vue';
import ResponsePanel from './ResponsePanel.vue';
import LanguageSwitch from './LanguageSwitch.vue';
import ModelSelection from './ModelSelection.vue';
import { message } from 'ant-design-vue';
import { streamPrompt, createPrompt } from './../services/api';
import { v4 as uuidv4 } from 'uuid';
import ChatMenu from './MainMenu.vue';  // Import ChatMenu
import { Tabs, TabPane } from 'ant-design-vue'; // Make sure Tabs and TabPane are imported
import { PlusOutlined, SettingOutlined } from '@ant-design/icons-vue';
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
    const { t } = useI18n();
    const prompt = ref('');
    const responses = ref([]);
    const loading = ref(false);
    const modelsStore = useModelsStore();
    const updateTrigger = ref(0);
    const storedPrompt = ref({status:'initialized', prompt:null, prompt_id:null});
    const drawerVisible = ref(false);



    const showDrawer = () => {
      drawerVisible.value = true;
    };


    const handleToolbarAction = ({ key }) => {
      if (key === 'new_chat') {
        console.log("New Chat Started");
        // Implement new chat initiation logic
      } else if (key === 'settings') {
        console.log("Settings Opened");
        // Implement settings adjustment logic
      }
    };

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

      await createPromptServerside();

      const serviceResponse = await modelsStore.getServiceResponse();

      if (!serviceResponse) {
        message.error(t('failed_to_retrieve_model_information'));
        loading.value = false;
        return;
      }

      const selectedModelInfo = modelsStore.selectedModels.map(modelId => {
        const fullModelInfo = serviceResponse.find(model => model.id === modelId);
        return fullModelInfo || { id: modelId, platform: 'unknown' };
      });

      const promptData = {
        prompt: prompt.value.trim(),
        models: selectedModelInfo,
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
      storedPrompt,
      handleKeydown,
      handleSubmit,
      updateTrigger,
      showDrawer,
      drawerVisible,
      handleToolbarAction,

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

.prompt_input {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  color: #444444;
  margin-top: 10px;
}

.textarea-container {
  clear: both;
}

.chat-area {
  width: 100%;
  max-width: 100%;
}
</style>
