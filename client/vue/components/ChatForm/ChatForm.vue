
<template>
  <v-layout ref="app">
    <AppBar/>
    <v-main>
      <v-row>
        <v-col :cols="11">
          <ModelSelectionDrawer/>
          <ResponsePanel v-if="!isComparisonViewVisible" :userContextList="userContextList" :loading="loading"/>
          <ComparisonTable v-if="isComparisonViewVisible" :userContextList="userContextList"/>
        </v-col>
        <v-col :cols="1">
          <ResponsePanelMenu :userContextList="userContextList" @delete-thread="showDeleteConfirmation"/>
        </v-col>
      </v-row>

    </v-main>
    <v-navigation-drawer location="end" name="drawer" permanent>
      <div class="d-flex justify-center align-top h-100">
        <PromptPanel :key="promptPanelUpdateTrigger"/>
      </div>
    </v-navigation-drawer>
    <v-footer name="footer" app>
      <v-container>
        <v-row>
          <v-col cols="11" md="9" sm="12" style="margin: 0;padding: 0">
            <v-form v-model="valid">
              <textarea
                  style="width: 100%;background: #292929"
                  v-model="prompt.prompt"
                  rows="auto"
                  :disabled="loading"
                  :spellcheck="false"
                  @keydown="handleKeydown"
              ></textarea>

            </v-form>
          </v-col>
          <v-col cols="3" md="3" sm="0">
            <div style="margin: -15px 0 0 10px;padding:0" class="text-primary">
              <v-btn
                  variant="text"
                  @click="showModelSelection"
              >
                {{ $t('selected_models', 'Selected Models') }}
              </v-btn>
              <ListModelSelection/>
            </div>
          </v-col>
        </v-row>
      </v-container>
    </v-footer>
    <v-snackbar
        v-model="snackbar.show"
        :color="snackbar.color"
        :timeout="snackbar.timeout">
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
import { onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { useModelsStore } from '../../stores/models.js';
import PromptPanel from '../ResponsePanel/PromptPanel.vue';
import ResponsePanel from '../ResponsePanel/ResponsePanel.vue';
import LanguageSwitch from '../LanguageSelection/LanguageSwitch.vue';
import ModelSelection from '../ModelSelection/ModelSelection.vue';
import ComparisonTable from '../ResponsePanel/ComparisonTable.vue';
import ThemeSwitch from '../ThemeSwitch/ThemeSwitch.vue';
import ResponsePanelMenu from "@/vue/components/ResponsePanel/ResponsePanelMenu.vue";
import {
  createPrompt,
  deleteUserContext,
  fetchUserContext,
  processChunk,
  saveUserContext,
  stream,
  exportUserContextToExel
} from '../../services/api.js';
import { v4 as uuidv4 } from 'uuid';
import { UserContext } from '../../models/UserContext.js';
import AppBar from "@/vue/components/AppBar/AppBar.vue";
import { useAuthStore } from "@/vue/stores/currentUser.js";
import ModelSelectionDrawer from "@/vue/components/ModelSelection/ModelSelectionDrawer.vue";
import ListModelSelection from "@/vue/components/ModelSelection/ListModelSelection.vue";

export default {
  name: 'ChatForm',
  components: {
    ModelSelectionDrawer,
    ListModelSelection,
    AppBar,
    ResponsePanelMenu,
    PromptPanel,
    ResponsePanel,
    LanguageSwitch,
    ModelSelection,
    ComparisonTable: ComparisonTable,
    ThemeSwitch
  },
  setup() {
    const authStore = useAuthStore();

    const initUserContext = () => {
      authStore.loadFromStorage().then(userData => {
        if (!userData) {
          console.error("No user in pinia storage");
        }
        user = userData?.accessToken?.user_info.uuid;
        fetchUserContext()
          .then(fetchUserContextCallback)
          .catch((error) => {
            showMessage(t('failed_to_retrieve_user_context'), 'error');
            console.error('Error retrieving user context:', error);
          })
          .finally(() => {
            hideLoader();
            triggerPromptPanelUpdate();
          });
      });
    }

    let user = null;

    const thread_id = 1;

    const streamRequestModel = {
      id: null,
      prompt: '',
      models: [],
      method_name: 'fetch_completion',
    };

    const getStreamPostRequestModel = (promptPostRequest, models, method_name = 'fetch_completion') => {
      const { uuid: id, prompt } = promptPostRequest;
      return { ...streamRequestModel, id, prompt, models, method_name };
    };

    const getPromptPostRequest = (uuid, user, prompt, status = 'INITIALIZED') => {
      return new UserContext.PromptPostRequestModel(uuid, prompt, user, status);
    };

    const prompt = ref(UserContext.PromptPostRequestModel);

    const userContextList = ref([]);
    const modelsStore = useModelsStore();

    const buffer = ref('');
    const loading = ref(false);

    const promptPanelUpdateTrigger = ref(0);

    const { t } = useI18n();
    const valid = ref(false);
    const isComparisonViewVisible = ref(false);
    const deleteDialog = ref(false);

    const toolCallRegister = ref([]);

    const snackbar = ref({
      show: false,
      text: '',
      color: 'info',
      timeout: 10000
    });

    const showMessage = (text, color = 'info') => {
      snackbar.value.show = true;
      snackbar.value.text = text;
      snackbar.value.color = color;
    };

    const handlePaste = (event) => {
      // Zugriff auf die eingefügten Daten
      const pastedData = (event.clipboardData || window.clipboardData).getData('text');
      console.log('Eingefügter Text:', pastedData);

      // Speichere den eingefügten Text im localStorage
      localStorage.setItem('savedPrompt', pastedData);

      // Setze den Wert des Textarea auf den eingefügten Text
      prompt.value.prompt = pastedData;
    };

    const handleBlur = () => {
  // Laden des gespeicherten Texts aus dem localStorage
  const savedText = localStorage.getItem('savedPrompt');

  // Setze den Text im Textarea nur, wenn ein gespeicherter Text vorhanden ist
  if (savedText !== null) {
    prompt.value.prompt = savedText;
  }
};

    watch(loading, (newValue) => {
      if (!newValue) {
        prompt.value.prompt = '';
      }
    });

    watch(prompt, (newValue) => {
      localStorage.setItem('savedPrompt', newValue.prompt);
    }, { deep: true });

    onMounted(() => {
      const savedPrompt = localStorage.getItem('savedPrompt');
      if (savedPrompt) {
        prompt.value.prompt = savedPrompt;
      }
      setTimeout(() => {
        initUserContext();
      }, 200);

      window.addEventListener('delete-thread', onDeleteThreadEvent);
      window.addEventListener('rerun-prompt', onRerunPrompt);
      window.addEventListener('comparison-open', onShowComparisonView);
      window.addEventListener('comparison-close', onHideComparisonView);
      window.addEventListener('usercontext-export-excel', onExportToExcel);
      window.addEventListener('show-message', onShowMessage);
    });

    onBeforeUnmount(() => {
      window.removeEventListener('delete-thread', onDeleteThreadEvent);
      window.removeEventListener('rerun-prompt', onRerunPrompt);
      window.removeEventListener('comparison-open', onShowComparisonView);
      window.removeEventListener('comparison-close', onHideComparisonView);
      window.removeEventListener('usercontext-export-excel', onExportToExcel);
      window.removeEventListener('show-message', onShowMessage);
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

    const onShowComparisonView = () => {
      isComparisonViewVisible.value = true;
    };

    const onHideComparisonView = () => {
      isComparisonViewVisible.value = false;
    };

    const showDeleteConfirmation = () => {
      deleteDialog.value = true;
    };

    const onRerunPrompt = async (event) => {
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

    const saveUserContextServerside = () => {
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
          (chunk, buffer) => processChunk(chunk, buffer, userContextList),
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
        //hideLoader();
      }
    };

    const onShowMessage = (event) => {
      showMessage(event.detail.message, event.detail.color);
    }

    const showModelSelection = () => {
      const event = new CustomEvent("open-model-selection", {});
      window.dispatchEvent(event);
    }

    const onExportToExcel = async () => {
      const user = userContextList.value[0]?.prompt.user;
      const thread_id = userContextList.value[0]?.thread_id;
      if (!user || !thread_id) {
        throw new Error("User or Thread ID not available.");
      }
      await exportUserContextToExel(user, thread_id)
    };

    const onDeleteThreadEvent = async (event) => {
      try {
        await deleteUserContext(event.detail.thread_id);
        userContextList.value = []
        showMessage(t('thread_deleted_successfully'), 'success');
      } catch (error) {
        showMessage(t('failed_to_delete_thread'), 'error');
        console.error('Error deleting thread:', error);
      }
    };

    return {
      handleKeydown,
      handleSubmit,
      handlePaste,
      handleBlur,
      promptPanelUpdateTrigger,
      t,
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
      showModelSelection
    };
  },
};
</script>
<style scoped>

textarea {
    width: 100%;
    min-height: 100px;
    max-height: 300px;
    resize: vertical;
    padding: 10px;
    font-size: 14px;
    color: #aaaaaa;
    border-radius: 10px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans', sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol', 'Noto Color Emoji';
}
</style>
