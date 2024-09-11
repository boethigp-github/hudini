<template>
  <v-dialog v-model="dialogVisible" max-width="600px">
    <v-card>
      <v-card-title>{{ $t('select_social_media', 'Select Social Media Accounts') }}</v-card-title>
      <v-card-text>
        <v-container>
          <!-- Telegram Group -->
          <v-row>
            <v-col>
              <h3>Telegram</h3>
              <v-checkbox
                  v-for="(account, index) in telegramAccounts"
                  :key="index"
                  :label="account.name"
                  v-model="selectedSocialMediaAccounts"
                  :value="account.id"
              />
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
import {ref, onMounted, onBeforeUnmount} from "vue";

export default {
  name: "SocialMediaModal",
  props: {},
  setup(props) {
    // Telegram accounts, these can be dynamically fetched as well
    const telegramAccounts = ref([
      {id: 1, name: "Telegram Account 1"},
      {id: 2, name: "Telegram Account 2"},
    ]);

    // Stores selected social media accounts
    const selectedSocialMediaAccounts = ref([]);

    const dialogVisible = ref(false)
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

    onMounted(() => {
      window.addEventListener('socialmedia-accounts-selection-open', onSocialMediaAccountSelectionOpen);
    });

    onBeforeUnmount(() => {
      window.removeEventListener('socialmedia-accounts-selection-open', onSocialMediaAccountSelectionOpen);
    });


    const onSocialMediaAccountSelectionOpen = () => {
      dialogVisible.value = true;
    }


    return {
      telegramAccounts,
      selectedSocialMediaAccounts,
      cancel,
      confirm,
      dialogVisible
    };
  },
};
</script>
