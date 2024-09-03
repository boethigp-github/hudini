<template>
  <a-layout>
    <a-layout-header :style="{background:'#e9edf2', padding:'0 5px 0 5px'}">
      <div style="display: block;min-height: 10px;cursor: pointer" class="chat-header">
        <div class="header">
          <img src="../assets/hidini2.webp" alt="Hudini Logo" class="logo" height="60"/>
          <ChatMenu/>
          <div class="language-switch-container">
            <LanguageSwitch/>
          </div>
        </div>
      </div>
    </a-layout-header>
    <a-layout :style="{background:'#e9edf2'}">
      <a-layout-content :style="{background:'#e9edf2', marginRight:'8px', width:'500px'}">
        <ResponsePanel :responses="responses" :loading="loading"/>
      </a-layout-content>
      <a-layout-sider width="25%" theme="light" :style="{background:'#e9edf2', width:'90%'}" :collapsed="false">
        <PromptPanel :key="updateTrigger"/>
      </a-layout-sider>
    </a-layout>
    <a-layout-footer :style="{background:'#e9edf2',marginTop:'-5px', padding:'5px'}">
      <a-tabs default-active-key="1" class="chat-tabs">
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
    </a-layout-footer>
  </a-layout>


</template>

<script>
import {onBeforeUnmount, onMounted, ref, watch} from 'vue';
import {useI18n} from 'vue-i18n';
import {useModelsStore} from './../stores/models';
import PromptPanel from './PromptPanel.vue';
import ArtifactsPanel from './ResponsePanel/ArtifactsPanels.vue';
import ResponsePanel from './ResponsePanel.vue';
import LanguageSwitch from './LanguageSwitch.vue';
import ModelSelection from './ModelSelection.vue';
import {message} from 'ant-design-vue';
import {
  stream,
  createPrompt,
  saveUserContext,
  fetchUserContext,
  processChunk,
  deleteUserContext
} from './../services/api';
import {v4 as uuidv4} from 'uuid';
import ChatMenu from './MainMenu.vue';
import {Tabs, TabPane, Button, Form, Input, Layout, Row, Col} from 'ant-design-vue';
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
    Button,
    Form,
    Input,
    Layout,
    Row,
    Col,
    ArtifactsPanel,
    PlusOutlined,
    SettingOutlined,
  },
  setup() {
    const uuid = uuidv4();
    const user = 1; // for now
    const thread_id = 1; // for now
    let userContextModel = {
      id: null,
      prompt_uuid: uuid,
      user: user,
      thread_id: thread_id,
      context_data: [],
      created: null,
      updated: null,
    };


    const buffer = ref('');
    const prompt = ref('');
    const responses = ref([]);
    const userContext = ref(userContextModel);
    const loading = ref(false);
    const modelsStore = useModelsStore();
    const updateTrigger = ref(0);
    const {t} = useI18n();

    // Function to update user context data
    const updateUserContextData = (value) => {
      userContext.value = value;
    }

    const PromptPostRequestModel = (uuid, model, promptValue) => {
      return {
        id: uuid,
        prompt: promptValue,
        models: [model], // Pass the current model configuration
        method_name: 'fetch_completion',
      };
    };

    // Function to handle keydown event
    const handleKeydown = (event) => {
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        handleSubmit();
      }
    };
    // Event handling for delete-thread
    onMounted(() => {
      window.addEventListener('delete-thread', deleteThread);
    });

    onBeforeUnmount(() => {
      window.removeEventListener('comparison-close', deleteThread);
    });

    const deleteThread = async () => {
      await deleteUserContext(userContext.value.id);
    };

    // Function to set responses
    const setResponses = (value) => {
      responses.value = value;
    }

    // Callback function for fetching user context
    const fetchUserContextCallback = async (userContextResponse) => {
      if (userContextResponse) {
        const userContext = await userContextResponse.json();
        if (userContextResponse.status === 200) {
          setResponses(userContext.context_data);
          updateUserContextData(userContext);
        }
      } else {
        message.error(t('failed_to_retrieve_user_context'));
      }
    };

    const postSaveUserContextCallback = () => {
      const callback = async () => {};
      userContext.value.context_data = responses.value;
      saveUserContext(userContext.value, callback).catch((error) => {
        console.error('Error sending responses to /usercontext:', error);
      });
    };

    // Fetch user context
    fetchUserContext(user, thread_id)
        .then(fetchUserContextCallback)
        .catch((error) => {
          message.error(t('failed_to_retrieve_user_context'));
          console.error('Error retrieving user context:', error);
        })
        .finally(() => {
          loading.value = false;
          updateTrigger.value++;
        });


    // Function to create prompt on the server side
    const createPromptServerside = async (uuid) => {
      const promptData = {
        prompt: prompt.value.trim(),
        user: 1,
        status: 'PROMPT_SAVED',
        uuid: uuid,
      };

      responses.value.push(promptData);
      updateTrigger.value++;

      try {
        await createPrompt(promptData);
      } catch (error) {
        message.error(t('failed_to_save_prompt'));
      }
    };

    // Function to handle prompt submission
    const handleSubmit = async () => {
      loading.value = true;
      createPromptServerside(uuid);
      for (const model of await modelsStore.getSelectedModelsWithMetaData()) {
        const generationRequest = PromptPostRequestModel(uuidv4(), model, prompt.value.trim());


        await stream(
            model.stream_url, // Use the stream URL from the selected model
            generationRequest,
            processChunk,
            buffer,
            responses,
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
              postSaveUserContextCallback();
            }
        );
      }
    };

    // Watcher to reset prompt after loading
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
      t,
      userContext,
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
  padding-right: 100px;
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
  top: 12px;
  background: darkgrey;
}

.send-button:hover {
  background: #1f2611;
}

.textarea-container {
  clear: both;
}


</style>
