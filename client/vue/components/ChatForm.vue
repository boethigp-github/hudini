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
    <a-layout>
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
import {ref, watch} from 'vue';
import {useI18n} from 'vue-i18n';
import {useModelsStore} from './../stores/models';
import PromptPanel from './PromptPanel.vue';
import ArtifactsPanel from './ResponsePanel/ArtifactsPanels.vue';
import ResponsePanel from './ResponsePanel.vue';
import LanguageSwitch from './LanguageSwitch.vue';
import ModelSelection from './ModelSelection.vue';
import {message} from 'ant-design-vue';
import {streamPrompt, createPrompt, sendResponsesToUserContext, fetchUserContext} from './../services/api';
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
    const {t} = useI18n();
    const prompt = ref('');
    const responses = ref([]);
    const loading = ref(false);

    const modelsStore = useModelsStore();
    const updateTrigger = ref(0);
    const buffer = ref(''); // Buffer to hold incomplete JSON strings


    const user = 1; // for now
    const thread_id = 1;

    /**
     * Fetch Usercontext and fill Responsepanel with thread data
     */
    fetchUserContext(user, thread_id)
        .then(userContext => {
          if (userContext) {
            // Initialize responses.value with the user context
            responses.value = userContext.map(contextItem => {
              return {
                prompt_id: contextItem.prompt_id,
                user: contextItem.user,
                status: contextItem.status,
                id: contextItem.id,
                prompt: contextItem.prompt,
                model: contextItem.model,
                completion: contextItem.completion,
              };
            });


            console.log("responses.value", userContext);
          } else {
            message.error(t('failed_to_retrieve_user_context'));
          }
        })
        .catch(error => {
          message.error(t('failed_to_retrieve_user_context'));
          console.error("Error retrieving user context:", error);
        })
        .finally(() => {
          loading.value = false;
          updateTrigger.value++
        });


    const createPromptServerside = async (id) => {
      if (!prompt.value || typeof prompt.value !== 'string' || prompt.value.trim() === '') {
        message.error(t('invalid_prompt'));
        return;
      }

      const promptData = {
        prompt: prompt.value.trim(),
        user: 1,
        status: 'prompt-saved',
        id: id,
      };

      responses.value.push(promptData);
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

          const responseIndex = responses.value.findIndex(
              r => r.id === responseModel.id && r.model === responseModel.model
          );

          if (responseIndex !== -1) {
            responses.value[responseIndex] = {
              ...responses.value[responseIndex],
              completion: responseModel.completion,
            };
          } else {
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

      function generateRandomNumberString(length) {
        let result = '';
        for (let i = 0; i < length; i++) {
          const randomDigit = Math.floor(Math.random() * 10); // Generates a random digit between 0 and 9
          result += randomDigit.toString();
        }
        return result;
      }

      const id = generateRandomNumberString(16);

      await createPromptServerside(id);

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
        id: id,
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

            // Wrap responses in the required format before sending
            const structuredResponse = {
              id: responses.value[0]['id'], // Directly access the id from the first response
              user: responses.value[0]['user'], // Directly access the id from the first response
              thread_id: 1, // Directly access the id from the first response
              context_data: responses.value, // Include all responses
            };


            // Send the structured response to /usercontext
            sendResponsesToUserContext(structuredResponse)
                .catch(error => {
                  console.error('Error sending responses to /usercontext:', error);
                });
          }
      );
    };

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
