<template>
  <v-dialog v-model="dialogVisible" max-width="600px">
    <v-card>
      <v-card-title>{{ $t('select_social_media', 'Select Social Media Accounts') }}</v-card-title>
      <v-card-text>
        <v-container>
          <h2>{{$t('provider', 'Provider')}}</h2><br/>
          <v-row v-for="(groups, provider) in groupedTelegramAccounts" :key="provider">
            <v-col>
              <v-row align="center">
                <component :is="groups.logo" class="provider-logo" />
                <h2>{{ provider }}</h2>
              </v-row>
              <v-row v-for="(accounts, groupName) in groups.groups" :key="groupName">
                <v-col>
                  <h4>{{$t('group', 'Group')}}: {{ groupName }}</h4>
                  <h5>{{$t('user', 'User')}}: {{ groupName }}</h5>
                  <v-checkbox
                      v-for="(account, index) in accounts"
                      :key="index"
                      :label="account.displayname"
                      v-model="selectedSocialMediaAccounts"
                      :value="account.id"
                  />
                </v-col>
              </v-row>
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
import {getTelegramAccounts} from './../../services/api'; // Import your API method
import TelegramLogo from './TelegramLogo.vue';

export default {
  name: "SocialMediaModal",

  components:{
    TelegramLogo
  },
  setup() {

    // Store for selected social media accounts
    const selectedSocialMediaAccounts = ref([]);
    const dialogVisible = ref(false);
    const groupedTelegramAccounts = ref({}); // Grouped accounts by provider and group

    // Fetch the Telegram accounts from the API only when the dialog is opened
    const fetchTelegramAccounts = async () => {
      try {
        const accounts = await getTelegramAccounts();
        groupAccountsByProviderAndGroup(accounts);
      } catch (error) {
        console.error("Failed to fetch telegram accounts:", error);
      }
    };

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
    const onSocialMediaAccountSelectionOpen = () => {
      dialogVisible.value = true;
    };

    onMounted(() => {
      window.addEventListener('socialmedia-accounts-selection-open', onSocialMediaAccountSelectionOpen);
    });

    onBeforeUnmount(() => {
      window.removeEventListener('socialmedia-accounts-selection-open', onSocialMediaAccountSelectionOpen);
    });

    // Cancel action
    const cancel = () => {
      const event = new CustomEvent('social-media-cancel', {});
      window.dispatchEvent(event);
    };

    // Confirm action, dispatch selected accounts via window event
    const confirm = () => {
      const event = new CustomEvent('social-media-confirm', {
        detail: {
          selectedAccounts: selectedSocialMediaAccounts.value,
        },
      });
      window.dispatchEvent(event);
    };

    // Watcher: Fetch accounts only when dialog is opened
    watch(dialogVisible, (newVal) => {
      if (newVal) {
        fetchTelegramAccounts();
      }
    });

    return {
      groupedTelegramAccounts,
      selectedSocialMediaAccounts,
      cancel,
      confirm,
      dialogVisible,
      getProviderLogo
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
