<template>
  <v-dialog v-model="dialogVisible" max-width="80%">
    <v-card>
      <v-card-title>{{ $t('select_social_media', 'Select Social Media Accounts') }}</v-card-title>
      <v-card-text>
        <v-container>
          <h2>{{ $t('provider', 'Provider') }}</h2><br/>
          <v-row v-for="(groups, provider) in groupedTelegramAccounts" :key="provider">
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
                      @update:selected="handleSelected"
                      item-props>
                    <template v-slot:subtitle="{ subtitle }">
                      <div v-html="subtitle"></div>
                    </template>
                  </v-list>
                </v-col>
              </v-row>
            </v-col>
            <v-col cols="9" md="9">
              <v-row>
                <v-col cols="12">
                  <v-text-field
                    v-model="imagePrompt"
                    :label="$t('image_prompt', 'Image Generation Prompt')"
                    variant="outlined"
                  ></v-text-field>
                </v-col>
                <v-col cols="12" class="d-flex justify-end">
                  <v-btn
                    color="primary"
                    @click="triggerGenerateImage"
                    :loading="isImageGenerating"
                    :disabled="!imagePrompt">
                    {{ $t('generate_image', 'Generate Image') }}
                  </v-btn>
                </v-col>
                <v-col cols="12">
                  <v-img
                    :width="300"
                    aspect-ratio="16/9"
                    cover
                     :src="generatedImageUrl">
                    <template v-slot:placeholder>
                      <v-row class="fill-height ma-0" align="center" justify="center">
                        <v-progress-circular indeterminate color="grey lighten-5"></v-progress-circular>
                      </v-row>
                    </template>
                  </v-img>
                  <p v-if="imageError" class="error--text">{{ imageError }}</p>
                </v-col>
                <v-col cols="12">
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
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="blue-darken-1" @click="cancel" :disabled="isLoading || isImageGenerating">{{ $t('cancel', 'Cancel') }}</v-btn>
        <v-btn color="primary" @click="confirm" :loading="isLoading" :disabled="isImageGenerating">{{ $t('publish', 'Publish') }}</v-btn>
      </v-card-actions>
      <v-progress-linear v-if="isLoading || isImageGenerating" color="primary" indeterminate></v-progress-linear>
    </v-card>
  </v-dialog>
</template>

<script>
import { markRaw, onBeforeUnmount, onMounted, ref, watch, nextTick } from "vue";
import { getTelegramAccounts, sendSocialMediaMessage, generateImage } from './../../services/api';
import TelegramLogo from './TelegramLogo.vue';
import AvatarComponent from './DummyAvatar.vue';
import { useI18n } from 'vue-i18n'
import { SocialMedia } from "@/vue/models/SocialMedia.js";

export default {
  name: "SocialMediaModal",
  components: {
    TelegramLogo,
    AvatarComponent
  },
  setup() {
    const {t} = useI18n();
    const dialogVisible = ref(false);
    const groupedTelegramAccounts = ref({});
    const selectedBotResponses = ref([]);
    const messageText = ref('');
    const selectedAccounts = ref([]);
    const isLoading = ref(false);
    const imagePrompt = ref('');
    const isImageGenerating = ref(false);
    const generatedImageUrl = ref('');
    const textareaWidth = ref(0);
    const messageTextarea = ref(null);
    const imageError = ref('');

    const fetchTelegramAccounts = async () => {
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
      groupedTelegramAccounts.value = providers;
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

    const cancel = () => {
      dialogVisible.value = false;
      imagePrompt.value = '';
      generatedImageUrl.value = '';
      imageError.value = '';
    };

    const getGroupByAccount = (accountId) => {
      for (const provider in groupedTelegramAccounts.value) {
        for (const groupName in groupedTelegramAccounts.value[provider].groups) {
          const account = groupedTelegramAccounts.value[provider].groups[groupName].find(acc => acc.id === accountId);
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
        for (const accountId of selectedAccounts.value) {
          const result = getGroupByAccount(accountId);
          if (result) {
            const {account, group, provider} = result;
            let message = messageText.value;
            if (generatedImageUrl.value) {
              message += `\n\n${generatedImageUrl.value}`;
            }
            const response = await sendSocialMediaMessage(
                provider,
                new SocialMedia.Message(account.displayname, accountId, group, message)
            );
            if (response && response.status === "Message sent successfully") {
              sentMessages.push({accountId, messageId: response.message_id});
            }
          } else {
            console.error(`No valid account or group found for account ID ${accountId}`);
          }
        }

        if (sentMessages.length > 0) {
          const messageIds = sentMessages.map(msg => `${msg.accountId}: ${msg.messageId}`).join(', ');
          window.dispatchEvent(new CustomEvent('show-message', {
            detail: {message: t('messages_sent_successfully', `Messages sent successfully. Message IDs: ${messageIds}`)}
          }));
        } else {
          window.dispatchEvent(new CustomEvent('show-message', {
            detail: {message: t('no_messages_sent', "No messages were sent successfully")}
          }));
        }
      } catch (error) {
        console.error("Error sending messages:", error);
        window.dispatchEvent(new CustomEvent('show-message', {
          detail: {message: t('error_sending_messages', "Error sending messages")}
        }));
      } finally {
        isLoading.value = false;
      }
    };

    const handleSelected = () => {
      console.log("selectedAccounts", selectedAccounts.value);
    };

    const handleImageError = (error) => {
      console.error("Error loading image:", error);
      imageError.value = t('error_loading_image', "Error loading image");
    };

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
          style: "vivid"
        });

        console.log("Image generation response:", response);

        if (response && response.data && response.data.length > 0) {
          generatedImageUrl.value = response.data[0].url;
          console.log("Generated image URL:", generatedImageUrl.value);
        } else {
          throw new Error("No image URL in the response");
        }
      } catch (error) {
        console.error("Error generating image:", error);
        imageError.value = t('error_generating_image', "Error generating image");
        window.dispatchEvent(new CustomEvent('show-message', {
          detail: {message: t('error_generating_image', "Error generating image")}
        }));
      } finally {
        isImageGenerating.value = false;
      }
    };

    watch(dialogVisible, (newVal) => {
      if (newVal) {
        fetchTelegramAccounts();
        nextTick(() => {
          if (messageTextarea.value) {
            textareaWidth.value = messageTextarea.value.$el.offsetWidth;
          }
        });
      } else {
        imagePrompt.value = '';
        generatedImageUrl.value = '';
        imageError.value = '';
      }
    });

    watch(generatedImageUrl, (newVal) => {
      console.log("Generated image URL updated:", newVal);
    });

    return {
      groupedTelegramAccounts,
      cancel,
      confirm,
      dialogVisible,
      getProviderLogo,
      getListItems,
      selectedAccounts,
      handleSelected,
      selectedBotResponses,
      messageText,
      isLoading,
      getGroupLink,
      imagePrompt,
      isImageGenerating,
      generatedImageUrl,
      triggerGenerateImage,
      messageTextarea,
      textareaWidth,
      imageError,
      handleImageError
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