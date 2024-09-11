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
                  <h4>{{ $t('group', 'Group') }}: {{ groupName }}</h4>
                  <h5>{{ $t('user', 'User') }}: {{ groupName }}</h5>
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
                  <v-textarea rows="20" width="100%" v-model="messageText" variant="filled" auto-grow counter>
                  </v-textarea>
                </v-col>
          </v-row>
        </v-container>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="blue-darken-1" @click="cancel">{{ $t('cancel', 'Cancel') }}</v-btn>
        <v-btn color="primary" @click="confirm">{{ $t('publish', 'Publish') }}</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
<script>
import {markRaw, onBeforeUnmount, onMounted, ref, watch} from "vue";
import {getTelegramAccounts, sendSocialMediaMessage} from './../../services/api'; // Import your API method
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
    const groupedTelegramAccounts = ref({}); // Grouped accounts by provider and group
    const selectedBotResponses=ref([])
    const messageText = ref('')
    // Fetch the Telegram accounts from the API only when the dialog is opened
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

    const selectedAccounts = ref([])


    // Group accounts by provider and group
    const groupAccountsByProviderAndGroup = (accounts) => {
      const providers = {};
      accounts.forEach(account => {
        const provider = account.provider; // Group by provider (e.g., 'telegram')
        if (!providers[provider]) {
          providers[provider] = {
            logo: getProviderLogo(provider),  // Assign logo based on provider dynamically
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

    // Function to dynamically get the provider logo
    const getProviderLogo = (provider) => {
      const logoMap = {
        telegram: markRaw(TelegramLogo),

        // Add more providers and their corresponding logos here
      };
      return logoMap[provider] || '/assets/default-logo.png';  // Fallback to a default logo
    };

    // Open modal event listener
    const onSocialMediaAccountSelectionOpen = (event) => {
      dialogVisible.value = true;
      selectedBotResponses.value=event.detail.selectedBotResponses
      messageText.value = selectedBotResponses.value.map(item=>item.content).join('\n');
    };

    onMounted(() => {
      window.addEventListener('socialmedia-accounts-selection-open', onSocialMediaAccountSelectionOpen);
    });

    onBeforeUnmount(() => {
      window.removeEventListener('socialmedia-accounts-selection-open', onSocialMediaAccountSelectionOpen);
    });

    // Cancel action
    const cancel = () => {
      dialogVisible.value=false
    };

    // Confirm action, dispatch selected accounts via window event
    const confirm = () => {


      console.log("selectedAccounts", selectedAccounts.value);

            if(!selectedAccounts.value.length) {
              window.dispatchEvent(new CustomEvent('show-message', {detail: {message: t('please_choose_a_user', "Please choose a user")}}));
            }

            selectedAccounts.value.forEach(account=>{
console.log("account", account);
              let group_id = '@hudinitests'
          sendSocialMediaMessage("telegram", new SocialMedia.Message(String(account), account, group_id, messageText.value ));
      })

    };

    // Watcher: Fetch accounts only when dialog is opened
    watch(dialogVisible, (newVal) => {
      if (newVal) {
        fetchTelegramAccounts();
      }
    });

    const handleSelected=()=>{

      console.log("selectedAccounts",selectedAccounts.value);

    }

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
      messageText
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
