<template>
  <v-layout ref="app">
    <v-app-bar class="v-app-bar" name="app-bar" density="compact">
      <v-container fluid>
        <v-row align="center" no-gutters>
          <v-col class="theme-switch-container" cols="auto">
            <ThemeSwitch/>
          </v-col>
          <v-spacer></v-spacer>
          <v-col class="language-switch-container" cols="auto">
            <LanguageSwitch/>
          </v-col>
        </v-row>
      </v-container>
    </v-app-bar>
    <v-navigation-drawer location="end" name="drawer" permanent>
      <div class="d-flex justify-center align-top h-100">
        <PromptPanel :key="promptPanelUpdateTrigger"/>
      </div>
    </v-navigation-drawer>
    <v-main>
      <v-row>
        <v-col :cols="11">
          <ResponsePanel v-if="!isComparisonViewVisible" :userContextList="userContextList" :loading="loading"/>
          <ComparisonDrawer v-if="isComparisonViewVisible" :userContextList="userContextList"/>
        </v-col>
        <v-col :cols="1">
          <ResponsePanelMenu :userContextList="userContextList" @delete-thread="showDeleteConfirmation"/>
        </v-col>
      </v-row>
    </v-main>

    <v-footer name="footer" app>
      <v-container>
        <v-row>
          <ModelSelection/>
        </v-row>
        <v-row>
          <v-col cols="12" md="12" style="margin: 0;padding: 0">
            <v-form v-model="valid">
              <v-textarea
                  v-model="prompt.prompt"
                  :label="t('enter_prompt')"
                  rows="2"
                  :disabled="loading"
                  :spellcheck="false"
                  @keydown="handleKeydown"
              ></v-textarea>
            </v-form>
          </v-col>
        </v-row>
      </v-container>
    </v-footer>


    <v-snackbar
        v-model="snackbar.show"
        :color="snackbar.color"
        :timeout="snackbar.timeout"
    >
      {{ snackbar.text }}
      <template v-slot:actions>
        <v-btn
            color="white"
            @click="snackbar.show = false">
        </v-btn>
      </template>
    </v-snackbar>
  </v-layout>
</template>

<script>
import {onBeforeUnmount, onMounted, ref, watch, reactive} from 'vue';
import {useI18n} from 'vue-i18n';
import {useModelsStore} from './../stores/models';
import PromptPanel from './PromptPanel.vue';
import ResponsePanel from './ResponsePanel.vue';
import LanguageSwitch from './LanguageSwitch.vue';
import ModelSelection from './ModelSelection.vue';
import ComparisonDrawer from './ResponsePanel/ComparisonTable.vue';
import ThemeSwitch from './ThemeSwitch.vue';
import ResponsePanelMenu from "@/vue/components/ResponsePanel/ResponsePanelMenu.vue";
import _ from 'lodash'
import {toRaw} from 'vue';
import {
  createPrompt,
  deleteUserContext,
  fetchUserContext,
  processChunk,
  saveUserContext,
  stream,
  exportUserContextToExel
} from './../services/api';
import {v4 as uuidv4} from 'uuid';
import {UserContext} from '../models/UserContext.js';

export default {
  name: 'ChatForm',
  components: {
    ResponsePanelMenu,
    PromptPanel,
    ResponsePanel,
    LanguageSwitch,
    ModelSelection,
    ComparisonDrawer,
    ThemeSwitch
  },
  setup() {
    const user = "5baab051-0c32-42cf-903d-035ec6912a91";
    const thread_id = 1;

    const streamRequestModel = {
      id: null,
      prompt: '',
      models: [],
      method_name: 'fetch_completion',
    };

    const getStreamPostRequestModel = (promptPostRequest, models, method_name = 'fetch_completion') => {
      const {uuid: id, prompt} = promptPostRequest;
      return {...streamRequestModel, id, prompt, models, method_name};
    };

    const getPromptPostRequest = (uuid, user, prompt, status = 'INITIALIZED') => {
      return new UserContext.PromptPostRequestModel(uuid, prompt, user, status);
    };


    const prompt = ref(UserContext.PromptPostRequestModel);
    const userContext = ref(null);
    const userContextList = ref([]);
    const modelsStore = useModelsStore();
    const buffer = ref('');
    const loading = ref(false);
    const promptPanelUpdateTrigger = ref(0);
    const {t} = useI18n();
    const valid = ref(false);
    const isComparisonViewVisible = ref(false);
    const deleteDialog = ref(false);

    const snackbar = ref({
      show: false,
      text: '',
      color: 'info',
      timeout: 3000
    });

    const showMessage = (text, color = 'info') => {
      snackbar.value.show = true;
      snackbar.value.text = text;
      snackbar.value.color = color;
    };

    watch(loading, (newValue) => {
      if (!newValue) {
        prompt.value.prompt = '';
      }
    });

    const updateUserContextList = (value) => {
      userContextList.value = value;
    };

    const handleKeydown = (event) => {
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        handleSubmit();
      }
    };

    const showComparisonView = () => {
      isComparisonViewVisible.value = true;
    };

    const hideComparisonView = () => {
      isComparisonViewVisible.value = false;
    };

    const resetUserContext = () => {
      userContext.value = new UserContext.UserContextPostRequestModel();
    };

    const showDeleteConfirmation = () => {
      deleteDialog.value = true;
    };


    const rerunPrompt = async (event) => {
      prompt.value.prompt = event.detail.prompt;
      handleSubmit();
    };

    const dispatchOnCompleteEvent = () => {
      const event = new CustomEvent("stream-complete", {});
      window.dispatchEvent(event);
    };

    const triggerPromptPanelUpdate = () => {
      promptPanelUpdateTrigger.value++;
    };

    const fetchUserContextCallback = async (userContextPostResponse) => {
      try {
        const userContextData = await userContextPostResponse.json();
        if (userContextPostResponse.status === 200) {
          updateUserContextList(userContextData);
        } else if (userContextPostResponse.status === 404) {
          // Handle 404 if needed
        } else {
          showMessage(t('failed_to_retrieve_user_context'), 'error');
          console.error(t('failed_to_retrieve_user_context'));
        }
      } catch (error) {
        showMessage(t('error_processing_user_context'), 'error');
        console.error('Error processing user context:', error);
      }
    };

    const saveUserContextServerside = (promptPostResponse) => {
      const callback = async (UserContextPostResponseModel) => {
        // Handle the response if needed
      };


      saveUserContext(JSON.stringify(userContextList.value), callback).catch((error) => {
        showMessage(t('error_saving_user_context'), 'error');
        console.error('Error sending responses to /usercontext:', error);
      });
    };

    async function streamGeneration(promptPostRequest) {
      for (const model of await modelsStore.getSelectedModelsWithMetaData()) {
        stream(
            model.stream_url,
            getStreamPostRequestModel(promptPostRequest, [model], "fetch_completion"),
            (chunk, buffer) => processChunk(chunk, buffer, userContext, userContextList),
            buffer,
            (error) => {
              console.error('Stream error:', error);
              showMessage(t('stream_error'), 'error');
              hideLoader();
            },
            () => {
              hideLoader();
            },
            () => {
              createPromptServerside(promptPostRequest).then(() => {
                setTimeout(() => {
                  saveUserContextServerside();
                  dispatchOnCompleteEvent();
                }, 200)
              });

              hideLoader();
            }
        );
      }
    }

    fetchUserContext(user, thread_id)
        .then(fetchUserContextCallback)
        .catch((error) => {
          showMessage(t('failed_to_retrieve_user_context'), 'error');
          console.error('Error retrieving user context:', error);
        })
        .finally(() => {
          hideLoader();
          triggerPromptPanelUpdate();
        });

    const createPromptServerside = async (promptPostRequest) => {
      triggerPromptPanelUpdate();
      return createPrompt(promptPostRequest);
    };

    const showLoader = () => {
      loading.value = true;
    };

    const hideLoader = () => {
      loading.value = false;
    };


    const initUserContexts = (promptPostRequest) => {
      const userContextValue = structuredClone(new UserContext.UserContextPostRequestModel(
          promptPostRequest.uuid,
          promptPostRequest.user,
          thread_id,
          structuredClone(new UserContext.UserContextPrompt(
              promptPostRequest.uuid,
              promptPostRequest.user,
              promptPostRequest.prompt,
              "INITIALIZED",
              Math.floor(Date.now() / 1000),
              []
          ))
      ));

      userContextList.value.push(userContextValue);
    };

    const handleSubmit = async () => {
      const promptPostRequest = getPromptPostRequest(uuidv4(), user, prompt.value.prompt.trim());
      initUserContexts(promptPostRequest);
      showLoader();
      try {
        await streamGeneration(promptPostRequest);


      } catch (error) {
        showMessage(t('error_submitting_prompt'), 'error');
        console.error('Error submitting prompt:', error);
      } finally {
        hideLoader();
      }
    };

    onMounted(() => {
      window.addEventListener('delete-thread', deleteThreadEvent);
      window.addEventListener('rerun-prompt', rerunPrompt);
      window.addEventListener('comparison-open', showComparisonView);
      window.addEventListener('comparison-close', hideComparisonView);
      window.addEventListener('usercontext-export-excel', exportToExcel);
    });

    onBeforeUnmount(() => {
      window.removeEventListener('delete-thread', deleteThreadEvent);
      window.removeEventListener('rerun-prompt', rerunPrompt);
      window.removeEventListener('comparison-open', showComparisonView);
      window.removeEventListener('comparison-close', hideComparisonView);
      window.removeEventListener('usercontext-export-excel', exportToExcel);
    });


    const exportToExcel = async () => {

        // Extract user and thread_id from the userContextList props
        const user = userContextList.value[0]?.prompt.user;
        const thread_id = userContextList.value[0]?.thread_id;

        if (!user || !thread_id) {
          throw new Error("User or Thread ID not available.");
        }

        await exportUserContextToExel(user, thread_id)
    };

    const deleteThreadEvent = async (event) => {
      try {
        await deleteUserContext(event.detail.thread_id);
        resetUserContext();
        showMessage(t('thread_deleted_successfully'), 'success');
      } catch (error) {
        showMessage(t('failed_to_delete_thread'), 'error');
        console.error('Error deleting thread:', error);
      }
    };
    return {
      handleKeydown,
      handleSubmit,
      promptPanelUpdateTrigger,
      t,
      userContext,
      prompt,
      loading,
      modelsStore,
      userContextList,
      valid,
      isComparisonViewVisible,
      snackbar,
      showMessage,
      deleteDialog,
      showDeleteConfirmation,

    };
  },
};
</script>

<style>
.v-app-bar {
  max-height: 48px;
  padding-top: 3px;
}

.theme-switch-container,
.language-switch-container {
  display: flex;
  align-items: center;
}

.theme-switch-container {
  margin-top: 15px;
}
</style>