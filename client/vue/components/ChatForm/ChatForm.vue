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
import {onBeforeUnmount, onMounted, ref, watch, reactive} from 'vue';
import {useI18n} from 'vue-i18n';
import {useModelsStore} from '../../stores/models.js';
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
import {v4 as uuidv4} from 'uuid';
import {UserContext} from '../../models/UserContext.js';
import AppBar from "@/vue/components/AppBar/AppBar.vue";
import {useAuthStore} from "@/vue/stores/currentUser.js";
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

    /**
     * Inits the user and its context
     */
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

    /**
     * Current user
     *
     * @type {null}
     */
    let user = null;

    /**
     * The identifier of a thread.
     *
     * @type {number}
     */
    const thread_id = 1;

    /**
     * @typedef {Object} StreamRequestModel
     * @property {null} id - The ID of the request. (Default: null)
     * @property {string} prompt - The prompt for the request. (Default: '')
     * @property {Array} models - The models to be used for the request. (Default: [])
     * @property {string} method_name - The name of the method to be used for fetching completion. (Default: 'fetch_completion')
     */
    const streamRequestModel = {
      id: null,
      prompt: '',
      models: [],
      method_name: 'fetch_completion',
    };

    /**
     * Represents a function that retrieves a Stream Post Request Model.
     *
     * @param {object} promptPostRequest - The Prompt Post Request object.
     * @param {object} models - The models object.
     * @param {string} [method_name='fetch_completion'] - The method name.
     * @returns {object} The Stream Post Request Model.
     */
    const getStreamPostRequestModel = (promptPostRequest, models, method_name = 'fetch_completion') => {
      const {uuid: id, prompt} = promptPostRequest;
      return {...streamRequestModel, id, prompt, models, method_name};
    };

    const getPromptPostRequest = (uuid, user, prompt, status = 'INITIALIZED') => {
      return new UserContext.PromptPostRequestModel(uuid, prompt, user, status);
    };

    /**
     * The `prompt` variable is a reference to the `PromptPostRequestModel` class
     * defined in the `UserContext` module.
     *
     * Use this variable to access and manipulate prompt post requests for user actions.
     *
     * @type {UserContext.PromptPostRequestModel}
     */
    const prompt = ref(UserContext.PromptPostRequestModel);

    /**
     * Represents a list of user context objects.
     *
     * @type {Array}
     */
    const userContextList = ref([]);
    /**
     * The `modelsStore` is a variable that represents a store for models.
     *
     * This variable is created by calling the `useModelsStore` function, which is expected to return the store for models.
     * The purpose of this store is to manage and store information about models in the application.
     *
     * The `modelsStore` variable should be used to access and manipulate models in the application.
     * It provides methods and properties to add, update, delete, and retrieve models from the store.
     *
     * Note that the specific implementation of the store will depend on the `useModelsStore` function.
     * It is recommended to check the documentation of the `useModelsStore` function for more details on how to work with the `modelsStore`.
     */
    const modelsStore = useModelsStore();

    /**
     * A variable representing a buffer reference.
     *
     * @type {string}
     * @name buffer
     * @memberOf module:buffer
     * @instance
     * @description
     * The `buffer` variable is a reference to a string value. It represents a buffer that can be used
     * to store and manipulate string data. The buffer is mutable, meaning its value can be changed
     * during the execution of the program.
     *
     * @example
     * // Assign a value to the buffer
     * buffer = 'This is a buffer';
     *
     * // Modify the buffer value
     * buffer = 'Updated buffer value';
     */
    const buffer = ref('');
    /**
     * Represents the current loading state.
     * @type {boolean}
     */
    const loading = ref(false);

    /**
     * Variable for tracking the number of times the prompt panel is updated.
     *
     * @type {number}
     * @name promptPanelUpdateTrigger
     * @default 0
     * @since 1.0.0
     */
    const promptPanelUpdateTrigger = ref(0);

    const {t} = useI18n();
    const valid = ref(false);
    const isComparisonViewVisible = ref(false);
    const deleteDialog = ref(false);

    /**
     * All tooling executions gets stored here
     *
     * @type {Ref<UnwrapRef<*[]>>}
     */
    const toolCallRegister = ref([]);

    const snackbar = ref({
      show: false,
      text: '',
      color: 'info',
      timeout: 10000
    });

    /**
     * Displays a message in a snackbar with the specified text and color.
     *
     * @param {string} text - The text to display in the snackbar.
     * @param {string} [color='info'] - The color of the snackbar. Defaults to 'info'.
     *                                  Possible values are: 'info', 'success', 'error', 'warning'.
     */
    const showMessage = (text, color = 'info') => {
      snackbar.value.show = true;
      snackbar.value.text = text;
      snackbar.value.color = color;
    };

    /**
     * Watches the `loading` variable and resets the prompt if loading is completed.
     * @param {Boolean} newValue - New value of the loading state.
     */
    watch(loading, (newValue) => {
      if (!newValue) {
        prompt.value.prompt = '';
      }
    });

    /**
     * Updates the userContextList with the provided value.
     * @param {Object} value - New value for the userContextList.
     */
    const updateUserContextList = (value) => {
      userContextList.value = value;
    };

    /**
     * Handles the keydown event and submits the form when the Enter key is pressed (without Shift).
     * @param {Event} event - The keyboard event.
     */
    const handleKeydown = (event) => {
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        handleSubmit();
      }
    };

    /**
     * Shows the comparison view.
     */
    const onShowComparisonView = () => {
      isComparisonViewVisible.value = true;
    };

    /**
     * Hides the comparison view.
     */
    const onHideComparisonView = () => {
      isComparisonViewVisible.value = false;
    };


    /**
     * Shows the delete confirmation dialog.
     */
    const showDeleteConfirmation = () => {
      deleteDialog.value = true;
    };

    /**
     * Reruns the prompt based on the event's detail.
     * @param {Event} event - The event containing the prompt details.
     */
    const onRerunPrompt = async (event) => {
      prompt.value.prompt = event.detail.prompt;
      handleSubmit();
    };

    /**
     * Dispatches a custom "stream-complete" event when the streaming process is finished.
     */
    const dispatchOnCompleteEvent = () => {
      const event = new CustomEvent("stream-complete", {});
      window.dispatchEvent(event);
    };

    /**
     * Triggers an update on the prompt panel by incrementing the update trigger value.
     */
    const triggerPromptPanelUpdate = () => {
      promptPanelUpdateTrigger.value++;
    };

    /**
     * Fetches the user context using the provided callback and processes the response.
     * @param {Object} userContextPostResponse - The response from the user context API.
     */
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

    /**
     * Saves the user context to the server by calling the saveUserContext function.
     */
    const saveUserContextServerside = () => {
      const callback = async (UserContextPostResponseModel) => {
        // Handle the response if needed
      };

      saveUserContext(JSON.stringify(userContextList.value), callback).catch((error) => {
        showMessage(t('error_saving_user_context'), 'error');
        console.error('Error sending responses to /usercontext:', error);
      });
    };

    /**
     * Handles the stream generation process for a prompt post request.
     * @param {Object} promptPostRequest - The request data for the prompt.
     */
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


    /**
     * Creates a prompt object
     *
     * @param promptPostRequest
     * @returns {Promise<Object>}
     */
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

    /**
     * Inits user account
     *
     * @param promptPostRequest
     */
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

    onMounted(async () => {
      setTimeout(() => {
        initUserContext();
      }, 200)

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

    const onShowMessage = (event) => {
      showMessage(event.detail.message, event.detail.color);
    }

    const showModelSelection = ()=>{
      const event = new CustomEvent("open-model-selection", {});
      window.dispatchEvent(event);
    }

    /**
     * Exports to excel
     *
     * @returns {Promise<void>}
     */
    const onExportToExcel = async () => {
      const user = userContextList.value[0]?.prompt.user;
      const thread_id = userContextList.value[0]?.thread_id;
      if (!user || !thread_id) {
        throw new Error("User or Thread ID not available.");
      }
      await exportUserContextToExel(user, thread_id)
    };

    /**
     * Deletes a thread
     *
     * @param event
     * @returns {Promise<void>}
     */
    const onDeleteThreadEvent = async (event) => {
      try {
        await deleteUserContext(event.detail.thread_id);
        userContextList.value=[]
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

