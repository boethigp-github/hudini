<template>
  <a-layout>
    <!-- Header Layout -->
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

    <!-- Main Content Layout -->
    <a-layout :style="{background:'#e9edf2'}">
      <a-layout-content :style="{background:'#e9edf2', marginRight:'8px', width:'500px'}">
        <ResponsePanel :responses="responses" :loading="loading"/>
      </a-layout-content>

      <!-- Sidebar Layout -->
      <a-layout-sider width="25%" theme="light" :style="{background:'#e9edf2', width:'90%'}" :collapsed="false">
        <PromptPanel :key="promptPanelUpdateTrigger"/>
      </a-layout-sider>
    </a-layout>

    <!-- Footer Layout -->
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
    const user = 1; // Currently hardcoded user ID
    const thread_id = 1; // Currently hardcoded thread ID

    // Initial user context model
    const userContextModel = {
      id: null,
      prompt_uuid: uuid,
      user: user,
      thread_id: thread_id,
      context_data: [],
      created: null,
      updated: null,
    };

    /**
     * Creates a prompt post request model.
     * @param {String} uuid - The UUID for the prompt.
     * @param {Object} model - The model configuration.
     * @param {String} promptValue - The prompt input from the user.
     * @returns {Object} - The request model for the prompt.
     */
    const PromptPostRequestModel = (uuid, model, promptValue) => {
      return {
        id: uuid,
        prompt: promptValue,
        models: [model], // Pass the current model configuration
        method_name: 'fetch_completion',
      };
    };


    // Reactive references for handling various state
    const buffer = ref('');
    const prompt = ref('');
    const responses = ref([]);
    const userContext = ref(userContextModel);
    const loading = ref(false);
    const modelsStore = useModelsStore();
    const promptPanelUpdateTrigger = ref(0);
    const {t} = useI18n();

    // Watcher to reset prompt input after loading completes
    watch(loading, (newValue) => {
      if (!newValue) {
        prompt.value = '';
      }
    });

    /**
     * Updates the user context data with the provided value.
     * @param {Object} value - The new user context data.
     */
    const updateUserContextData = (value) => {
      userContext.value = value;
    };


    /**
     * Handles the keydown event for the prompt input.
     * Submits the prompt when the Enter key is pressed without Shift.
     * @param {Event} event - The keydown event.
     */
    const handleKeydown = (event) => {
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        handleSubmit();
      }
    };

    /**
     * Mount lifecycle hook to set up event listeners.
     * Registers a listener for the "delete-thread" event.
     */
    onMounted(() => {
      window.addEventListener('delete-thread', deleteThreadEvent);
      window.addEventListener('rerun-prompt', rerunPrompt);
    });

    /**
     * Before unmount lifecycle hook to clean up event listeners.
     * Removes the listener for the "delete-thread" event.
     */
    onBeforeUnmount(() => {
      window.removeEventListener('delete-thread', deleteThreadEvent);
      window.removeEventListener('rerun-prompt', rerunPrompt);
    });

    /**
     * resets user context
     */
    const resetUserContext = () => {
      userContext.value = userContextModel
    }
    /**
     * Deletes the current thread by calling the API.
     * Triggered by the "delete-thread" event.
     */
    const deleteThreadEvent = async () => {

      await deleteUserContext(userContext.value.id);
      resetUserContext()
      setResponses([])
    };
    /**
     *Reruns prompt.
     * Triggered by the rerun-prompr" event.
     */
    const rerunPrompt = async (event) => {
      console.log("rerun: ", prompt)
      prompt.value = event.detail.prompt;
      handleSubmit()
    };

    /**
     * Sets the responses data.
     * @param {Array} value - The new responses to set.
     */
    const setResponses = (value) => {
      responses.value = value;
    };

    /**
     * Triggers prompt panel update
     */
    const triggerPromptPanelUpdate = () => {
      promptPanelUpdateTrigger.value++;
    }
    /**
     * Callback function for handling the fetched user context.
     * Updates the responses and user context data.
     * @param {Response} userContextResponse - The response from the user context fetch API.
     */
    const fetchUserContextCallback = async (userContextResponse) => {
      const userContext = await userContextResponse.json();
      if (userContextResponse.status === 200) {
        setResponses(userContext.context_data);
        updateUserContextData(userContext);
      }
      else if (userContextResponse.status === 404) {
        console.log('Info: usercontext empty');
      } else {
        message.error(t('failed_to_retrieve_user_context'));
        console.error(t('failed_to_retrieve_user_context'));
      }
    };

    /**
     * Callback function for saving user context after response.
     * Calls the API to save the current user context.
     */
    const postSaveUserContextCallback = () => {
      const callback = async () => {
      } //@todo: calls pina usercontext storage
      userContext.value.context_data = responses.value;
      saveUserContext(userContext.value, callback).catch((error) => {
        console.error('Error sending responses to /usercontext:', error);
      });
    };

    /**
     * Wired stuff
     * @param promptValue
     * @returns {Promise<void>}
     */
    async function processGenerationStreaming(promptValue) {
      for (const model of await modelsStore.getSelectedModelsWithMetaData()) {
        const generationRequest = PromptPostRequestModel(uuidv4(), model, promptValue);
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
              hideLoader();
            },
            () => {
              hideLoader();
              postSaveUserContextCallback();
            }
        );
      }
    }

    /**
     * Fetches the user context from the server.
     * Handles loading state and triggers an update when complete.
     */
    fetchUserContext(user, thread_id)
        .then(fetchUserContextCallback)
        .catch((error) => {
          message.error(t('failed_to_retrieve_user_context'));
          console.error('Error retrieving user context:', error);
        })
        .finally(() => {
          hideLoader();
          triggerPromptPanelUpdate()
        });

    /**
     * Creates a prompt on the server side.
     * Sends the current prompt data to the server.
     * @param {String} uuid - The UUID of the prompt.
     */
    const createPromptServerside = async (uuid) => {
      const promptData = {
        prompt: prompt.value.trim(),
        user: 1,
        status: 'PROMPT_SAVED',
        uuid: uuid,
      };
      responses.value.push(promptData);
      triggerPromptPanelUpdate()
      await createPrompt(promptData);
    };

    /**
     * Show loader
     */
    const showLoader = () => {
      loading.value = true
    }

    /**
     * Hides loader
     */
    const hideLoader = () => {
      loading.value = false
    }


    /**
     * Handles the submission of the prompt.
     * Sends the prompt to the server and handles streaming responses.
     */
    const handleSubmit = async () => {
      const promptValue = prompt.value.trim();
      showLoader()
      createPromptServerside(uuid);
      processGenerationStreaming(promptValue);
    };


    return {
      handleKeydown,
      handleSubmit,
      promptPanelUpdateTrigger,
      t,
      userContext,
      prompt,
      responses,
      loading,
      modelsStore,
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
