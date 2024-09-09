<template>

  <v-layout ref="app">
 <v-app-bar class="v-app-bar " name="app-bar" density="compact">
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
          <ResponsePanel :userContextList="userContextList" :loading="loading"/>
        </v-col>
        <v-col :cols="1">
          <ResponsePanelMenu/>
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
  </v-layout>

  <ComparisonDrawer :responses="[]" width="90%"/>
</template>

<script>
import {onBeforeUnmount, onMounted, ref, watch} from 'vue';
import {useI18n} from 'vue-i18n';
import {useModelsStore} from './../stores/models';
import PromptPanel from './PromptPanel.vue';
import ResponsePanel from './ResponsePanel.vue';
import LanguageSwitch from './LanguageSwitch.vue';
import ModelSelection from './ModelSelection.vue';
import ComparisonDrawer from './ResponsePanel/ComparisonDrawer.vue';
import ThemeSwitch from './ThemeSwitch.vue';

import {
  createPrompt,
  deleteUserContext,
  fetchUserContext,
  processChunk,
  saveUserContext,
  stream
} from './../services/api';
import {useTheme} from 'vuetify'
import {v4 as uuidv4} from 'uuid';
import ChatMenu from './MainMenu.vue';
import {UserContext} from '../models/UserContext.js';
import ResponsePanelMenu from "@/vue/components/ResponsePanel/ResponsePanelMenu.vue";

export default {
  name: 'ChatForm',
  components: {
    ResponsePanelMenu,
    PromptPanel,
    ResponsePanel,
    LanguageSwitch,
    ModelSelection,
    ChatMenu,
    ComparisonDrawer,
    ThemeSwitch
  },
  setup() {

    const user = "5baab051-0c32-42cf-903d-035ec6912a91"; // Currently hardcoded user ID
    const thread_id = 1; // Currently hardcoded thread ID

    /**
     * Stream request moel
     * @type {{models: *[], method_name: string, id: (`${string}-${string}-${string}-${string}-${string}`|*|string), prompt: string}}
     */
    const streamRequestModel = {
      id: null,
      prompt: '',
      models: [], // Pass the current model configuration
      method_name: 'fetch_completion',
    };


    /**
     * Creates a stream request model
     *
     * @param promptPostRequest
     * @param models
     * @param method_name
     * @returns {{models: *[], method_name: string, id: (`${string}-${string}-${string}-${string}-${string}`|*|string), prompt: *}}
     * @constructor
     */
    const getStreamPostRequestModel = (promptPostRequest, models, method_name = 'fetch_completion') => {
      const {uuid: id, prompt} = promptPostRequest

      return {...streamRequestModel, id, prompt, models, method_name};
    };

    /**
     * Requestmodel for saving prompts
     *
     * @param uuid
     * @param user
     * @param prompt
     * @param status
     * @returns {UserContext.PromptPostRequestModel}
     */
    const getPromptPostRequest = (uuid, user, prompt, status = 'INITIALIZED') => {
      return new UserContext.PromptPostRequestModel(uuid, prompt, user, status);
    };


    const prompt = ref(UserContext.PromptPostRequestModel);
    const userContext = ref(UserContext.UserContextPostRequestModel);
    const userContextList = ref([UserContext.UserContextPostRequestModel]);
    const modelsStore = useModelsStore();
    const buffer = ref('');

    const loading = ref(false);
    const promptPanelUpdateTrigger = ref(0);
    const {t} = useI18n();
    const valid = ref(false)

    // Watcher to reset prompt input after loading completes
    watch(loading, (newValue) => {
      if (!newValue) {
        prompt.value.prompt = '';
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
      userContext.value = new UserContext.UserContextPostRequestModel()
    }
    /**
     * Deletes the current thread by calling the API.
     * Triggered by the "delete-thread" event.
     */
    const deleteThreadEvent = async () => {

      await deleteUserContext(userContext.value.thread_id);
      resetUserContext()

    };
    /**
     *Reruns prompt.
     * Triggered by the rerun-prompt" event.
     */
    const rerunPrompt = async (event) => {
      prompt.value.prompt = event.detail.prompt;
      handleSubmit().then()
    };

    /**
     * on stream complete
     */
    const dispatchOnCompleteEvent = () => {
      const event = new CustomEvent("stream-complete", {});
      window.dispatchEvent(event);
    }


    /**
     * Triggers prompt panel update
     */
    const triggerPromptPanelUpdate = () => {
      promptPanelUpdateTrigger.value++;
    }
    /**
     * Callback function for handling the fetched user context.
     * Updates the responses and user context data.
     * @param {Response} userContextPostResponse - The response from the user context fetch API.
     */
    const fetchUserContextCallback = async (userContextPostResponse) => {
      const userContext = await userContextPostResponse.json();
      if (userContextPostResponse.status === 200) {
        updateUserContextData(userContext);
      } else if (userContextPostResponse.status === 404) {

      } else {
        message.error(t('failed_to_retrieve_user_context'));
        console.error(t('failed_to_retrieve_user_context'));
      }
    };

    /**
     * Callback function for saving user context after response.
     * Calls the API to save the current user context.
     */
    const saveUserContextServerside = (promptPostResponse) => {
      const callback = async (UserContextPostResponseModel) => {
      } //@todo: calls pina usercontext storage
      prepareUserContextForPosting(promptPostResponse);
      saveUserContext(userContext.value, callback).catch((error) => {
        console.error('Error sending responses to /usercontext:', error);
      });
    };

    /**
     * Build userContext prompt
     * @param promptPostResponse
     * @returns {unknown}
     */
    const getUserContextPrompt = (promptPostResponse) => {
      const user_context_prompt = structuredClone(promptPostResponse);

      return user_context_prompt
    }

    /**
     * maps responses to context and sets uuid
     * @param promptPostResponse
     */
    const prepareUserContextForPosting = (promptPostResponse) => {


      console.log("prepareUserContextForPosting: promptPostResponse.uuid:", promptPostResponse.uuid);

      userContext.value = new UserContext.UserContextPostRequestModel(
          promptPostResponse.uuid,
          promptPostResponse.user,
          thread_id,
          getUserContextPrompt(promptPostResponse)
      )
    }


    /**
     * Wired stuff
     * @returns {Promise<void>}
     */
    async function streamGeneration(promptPostRequest) {
      for (const model of await modelsStore.getSelectedModelsWithMetaData()) {
         stream(
            model.stream_url, // Use the stream URL from the selected model
            getStreamPostRequestModel(promptPostRequest, [model], "fetch_completion"),
            (chunk, buffer) => processChunk(chunk, buffer, userContext, userContextList),
            buffer,
            (error) => {
              console.error('Stream error:', error);
              hideLoader()
            },
            () => {
              hideLoader()
            },
            ()=>{
                  hideLoader();
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
     * @param promptPostRequest
     */
    const createPromptServerside = async (promptPostRequest) => {
      triggerPromptPanelUpdate()
      return createPrompt(promptPostRequest);
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
     * Sets userContexts
     *
     * @param promptPostRequest
     */
    const initUserContexts = (promptPostRequest) => {
      userContext.value = new UserContext.UserContextPostRequestModel
      (
          promptPostRequest.uuid,
          promptPostRequest.user,
          thread_id,
          new UserContext.UserContextPrompt
          (
              promptPostRequest.uuid,
              promptPostRequest.user,
              promptPostRequest.prompt,
              "INITIALIZED",
              null,
              []
          ),
      );

      userContextList.value.push(userContext.value);
    }

    /**
     * Handles the submission of the prompt.
     * Sends the prompt to the server and handles streaming responses.
     */
    const handleSubmit = async () => {
      const promptPostRequest = getPromptPostRequest(uuidv4(), user, prompt.value.prompt.trim())
      initUserContexts(promptPostRequest);
      showLoader()
      streamGeneration(promptPostRequest).then(async () => {
        createPromptServerside(promptPostRequest).then(promptPostResponse => {
          //saveUserContextServerside(promptPostResponse);
          dispatchOnCompleteEvent()
        });
      });
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
    };
  },
};
</script>

<style>



.v-app-bar {
  max-height: 48px;
  padding-top:3px;
}

.theme-switch-container,
.language-switch-container {
  display: flex;
  align-items: center;
}

.theme-switch-container{
  margin-top: 15px;
}


</style>
