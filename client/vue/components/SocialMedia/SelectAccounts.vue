<template>
  <v-dialog v-model="dialogVisible" max-width="80%">
    <v-card>
      <v-card-title class="d-flex justify-space-between align-center">
        {{ $t('select_social_media', 'Select Social Media Accounts') }}
        <v-btn icon @click="cancel">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>
      <v-card-text>
        <v-container>
          <v-row v-for="(groups, provider) in groupedSocialMediaAccounts" :key="provider">
            <v-col cols="3" md="3">
              <v-row align="center">
                <component :is="groups.logo" class="provider-logo"/>
                <h2>{{ provider }}</h2>
              </v-row>
              <v-row v-for="(accounts, groupName) in groups.groups" :key="groupName">
                <v-col>
                  <h4>
                    {{ $t('group', 'Group') }}:
                    <a v-if="provider === 'telegram'" :href="getGroupLink(groupName)" target="_blank">
                      {{ groupName }}
                    </a>
                    <span v-else>{{ groupName }}</span>
                  </h4>
                  <v-list
                      :items="getListItems(accounts, groupName)"
                      lines="three"
                      :mandatory="true"
                      v-model:selected="selectedAccounts"
                      item-props>
                    <template v-slot:subtitle="{ subtitle }">
                      <div v-html="subtitle"></div>
                    </template>
                  </v-list>
                </v-col>
              </v-row>
            </v-col>
            <v-col cols="9" md="9">
              <v-row style="margin-top: -80px">
                <v-col cols="12">
                  <v-img
                      :width="200"
                      aspect-ratio="16/9"
                      cover
                      :src="generatedImageUrl"
                      @click="openImageModal"
                      style="cursor: pointer;"
                  />
                </v-col>
                <v-col cols="12">
                  <v-text-field
                      v-model="imagePrompt"
                      :label="$t('image_prompt', 'Image Generation Prompt')"
                      @keydown.enter="triggerGenerateImage"
                      variant="outlined">
                    <v-progress-linear v-if="isImageGenerating" color="primary" indeterminate></v-progress-linear>
                  </v-text-field>
                </v-col>
                <v-col cols="12">
                  <v-card-actions>
                    <v-btn color="blue-darken-1" @click="cancel" :disabled="isLoading || isImageGenerating">
                      {{ $t('cancel', 'Cancel') }}
                    </v-btn>
                    <v-btn color="primary" @click="confirm" :loading="isLoading" :disabled="isImageGenerating">
                      {{ $t('publish', 'Publish') }}
                    </v-btn>
                  </v-card-actions>
                  <v-textarea
                      ref="messageTextarea"
                      rows="20"
                      v-model="messageText"
                      variant="filled"
                      auto-grow
                      counter
                  ></v-textarea>
                </v-col>
              </v-row>
            </v-col>
          </v-row>
        </v-container>
      </v-card-text>
    </v-card>
  </v-dialog>

  <v-dialog v-model="imageModalVisible" max-width="90%">
    <v-card>
      <v-card-actions>
        <v-card-title class="headline d-flex justify-space-between align-center">
          {{ $t('full_size_image', 'Full Size Image') }}
        </v-card-title>
        <v-spacer></v-spacer>
        <v-btn color="primary" @click="closeImageModal">
          {{ $t('close', 'Close') }}
        </v-btn>
      </v-card-actions>

      <v-card-text>
        <v-img
            :src="generatedImageUrl"
            max-height="80vh"
            contain
        />
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="primary" @click="closeImageModal">
          {{ $t('close', 'Close') }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import {markRaw, onBeforeUnmount, onMounted, ref, watch} from "vue";
import {
  getTelegramAccounts,
  sendSocialMediaMessage,
  sendSocialMediaImageMessage,
  generateImage
} from './../../services/api';
import TelegramLogo from './TelegramLogo.vue';
import AvatarComponent from './DummyAvatar.vue';
import {useI18n} from 'vue-i18n'
import {SocialMedia} from "@/vue/models/SocialMedia.js";

export default {
  name: "SocialMediaModal",
  components: {
    TelegramLogo,
    AvatarComponent
  },
  setup() {
    const {t} = useI18n();
    const dialogVisible = ref(false);
    const imageModalVisible = ref(false);
    const groupedSocialMediaAccounts = ref({});
    const selectedBotResponses = ref([]);
    const messageText = ref('');
    const selectedAccounts = ref([]);
    const isLoading = ref(false);
    const imagePrompt = ref('');
    const isImageGenerating = ref(false);
    const generatedImageUrl = ref('');

    const messageTextarea = ref(null);
    const imageError = ref('');

    const fetchSocialMediaAccounts = async () => {
      try {
        const accounts = await getTelegramAccounts();
        groupAccountsByProviderAndGroup(accounts);
      } catch (error) {
        console.error("Failed to fetch telegram accounts:", error);
      }
    };

    const getListItems = (accounts, groupName) => {
      return accounts.map(account => ({
        prependAvatar: 'https://cdn.vuetifyjs.com/images/lists/1.jpg',
        title: account.displayname,
        subtitle: `<div>${groupName}</div>`,
        value: account.id
      }));
    };

    const groupAccountsByProviderAndGroup = (accounts) => {
      const providers = {};
      accounts.forEach(account => {
        const provider = account.provider;
        if (!providers[provider]) {
          providers[provider] = {
            logo: getProviderLogo(provider),
            groups: {}
          };
        }
        account.groups.forEach(group => {
          if (!providers[provider].groups[group]) {
            providers[provider].groups[group] = [];
          }
          providers[provider].groups[group].push(account);
        });
      });
      groupedSocialMediaAccounts.value = providers;
    };

    const getProviderLogo = (provider) => {
      const logoMap = {
        telegram: markRaw(TelegramLogo),
      };
      return logoMap[provider] || '/assets/default-logo.png';
    };

    const getGroupLink = (groupName) => {
      return `https://t.me/${groupName.replace('@', '')}`;
    };

    const onSocialMediaAccountSelectionOpen = (event) => {
      dialogVisible.value = true;
      selectedBotResponses.value = event.detail.selectedBotResponses
      messageText.value = selectedBotResponses.value.map(item => item.content).join('\n');
    };

    onMounted(() => {
      window.addEventListener('socialmedia-accounts-selection-open', onSocialMediaAccountSelectionOpen);
    });

    onBeforeUnmount(() => {
      window.removeEventListener('socialmedia-accounts-selection-open', onSocialMediaAccountSelectionOpen);
    });

    const sendMessageSuccess = (sentMessages) => {
      const messageIds = sentMessages.map(msg => `${msg.accountId}: ${msg.messageId}`).join(', ');
      window.dispatchEvent(new CustomEvent('show-message', {
        detail: {
          color: 'success',
          message: t('messages_sent_successfully', `Messages sent successfully. Message IDs: ${messageIds}`)
        }
      }));
    }

    const sendMessagesNoMessagesSended = (errors) => {
      window.dispatchEvent(new CustomEvent('show-message', {
        detail: {message: errors.join(","), color: 'error'}
      }));
    }

    const cancel = () => {
      dialogVisible.value = false;
      imagePrompt.value = '';
      generatedImageUrl.value = '';
      imageError.value = '';
    };

    const getGroupByAccount = (accountId) => {
      for (const provider in groupedSocialMediaAccounts.value) {
        for (const groupName in groupedSocialMediaAccounts.value[provider].groups) {
          const account = groupedSocialMediaAccounts.value[provider].groups[groupName].find(acc => acc.id === accountId);
          if (account && account.groups && account.groups.length > 0) {
            return {
              account: account,
              group: account.groups[0],
              provider: provider
            };
          }
        }
      }
      return null;
    };

    function sendMessagesError(error) {
      console.error("Error sending messages:", error);
      window.dispatchEvent(new CustomEvent('show-message', {
        detail: {message: error, color: 'error'}
      }));
    }

    function isSendMessagesResponseOkay(response) {
      return response && (response.status === "Image sent successfully" || response.status === "Message sent successfully");
    }

    const confirm = async () => {
      if (!selectedAccounts.value.length) {
        window.dispatchEvent(new CustomEvent('show-message', {
          detail: {message: t('please_choose_a_user', "Please choose a user")}
        }));
        return;
      }

      isLoading.value = true;

      try {
        const sentMessages = [];
        const errors = [];
        for (const accountId of selectedAccounts.value) {
          const result = getGroupByAccount(accountId);
          const {account, group, provider} = result;
          let message = messageText.value;

          const messageData = {
            user: account.displayname,
            api_id: accountId,
            group_id: group,
            caption: message,
            url: generatedImageUrl.value
          };

          if (!generatedImageUrl.value) {
            let response = await sendSocialMediaMessage(
                provider,
                new SocialMedia.Message(messageData.user, messageData.api_id, messageData.group_id, messageData.caption)
            );
            sentMessages.push({accountId, messageId: response.message_id});
            continue;
          }

          let response = await sendSocialMediaImageMessage(provider, messageData);

          if (isSendMessagesResponseOkay(response)) {
            sentMessages.push({accountId, messageId: response.message_id});
          }

          if (response.detail) {
            errors.push(response.detail);
          }
        }

        if (sentMessages.length > 0) {
          sendMessageSuccess(sentMessages);
        } else {
          sendMessagesNoMessagesSended(errors);
        }
      } catch (error) {
        sendMessagesError(error);
      } finally {
        isLoading.value = false;
      }
    };

    const handleImageError = (error) => {
      console.error("Error loading image:", error);
      imageError.value = t('error_loading_image', "Error loading image");
    };

    function sendGenerationError(error) {
      imageError.value = t('error_generating_image', "Error generating image");
      window.dispatchEvent(new CustomEvent('show-message', {
        detail: {message: imageError.value + " Error:" + error, color: 'error'}
      }));
    }

    const triggerGenerateImage = async () => {
      if (!imagePrompt.value) {
        window.dispatchEvent(new CustomEvent('show-message', {
          detail: {message: t('please_enter_image_prompt', "Please enter an image prompt")}
        }));
        return;
      }

      isImageGenerating.value = true;
      imageError.value = '';

      try {
        const response = await generateImage({
          prompt: imagePrompt.value,
          n: 1,
          size: "1024x1024",
          quality: "standard",
          style: "natural"
        });

        if (response && response.data && response.data.length > 0) {
          generatedImageUrl.value = response.data[0].url;
          console.log("Generated image URL:", generatedImageUrl.value);
        } else {
          throw new Error(response.detail);
        }
      } catch (error) {
        sendGenerationError(error);
      } finally {
        isImageGenerating.value = false;
      }
    };

    const openImageModal = () => {
      if (generatedImageUrl.value) {
        imageModalVisible.value = true;
      }
    };

    const closeImageModal = () => {
      imageModalVisible.value = false;
    };

    watch(dialogVisible, (newVal) => {
      if (newVal) {
        fetchSocialMediaAccounts();
      } else {
        imagePrompt.value = '';
        generatedImageUrl.value = '';
        imageError.value = '';
      }
    });

    return {
      groupedSocialMediaAccounts,
      cancel,
      confirm,
      dialogVisible,
      getProviderLogo,
      getListItems,
      selectedAccounts,
      selectedBotResponses,
      messageText,
      isLoading,
      getGroupLink,
      imagePrompt,
      isImageGenerating,
      generatedImageUrl,
      triggerGenerateImage,
      messageTextarea,
      imageError,
      handleImageError,
      imageModalVisible,
      openImageModal,
      closeImageModal
    };
  },
};
</script>

<style scoped>
.provider-logo {
  width: 32px;
  height: 32px;
  margin-right: 8px;
}
</style>