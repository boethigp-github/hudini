<template>
  <v-container class="panel-menu" v-if="userContextList.length">
    <v-row>
      <v-btn
          class="panel-menu-button"
          :icon="isComparisonOpen ? 'mdi-close' : 'mdi-select-compare'"
          :title="isComparisonOpen ? $t('close_comparison', 'Close comparison') : $t('comparison_view', 'Comparison view')"
          key="sub1"
          @click="toggleComparison"
          :color="isComparisonOpen ? 'primary' : 'default'"
      ></v-btn>
    </v-row>
    <v-row>
      <v-btn
          class="panel-menu-button"
          icon="mdi-delete-circle"
          :title="$t('delete_thread', 'Delete thread')"
          key="delete_thread"
          @click="openDeleteDialog"
      ></v-btn>
    </v-row>
     <v-row v-if="selectedBotResponses.length">
      <v-btn
          class="panel-menu-button"
          icon="mdi-account-group"
          :title="$t('publish_social_media', 'Publish in social media')"
          key="publish_social_media"
          @click="publishSocialMedia"
      ></v-btn>
    </v-row>


    <v-row  v-if="!selectedBotResponses.length">
      <v-btn
          class="panel-menu-button"
          icon="mdi-microsoft-excel"
          :title="$t('export_to_excel', 'Export to excel')"
          key="delete_thread"
          @click="exportToExcel"
      ></v-btn>
    </v-row>

    <v-dialog v-model="deleteDialog" max-width="600px">
      <v-card>
        <v-card-title>{{
            $t('delete_thread_confirmation_title', 'Are you sure you want to delete this thread?')
          }}
        </v-card-title>
        <v-card-text>{{ $t('delete_thread_confirmation_content', 'This action cannot be undone.') }}</v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue-darken-1" @click="cancelDelete">{{
              $t('delete_thread_cancel_text', 'No, keep it')
            }}
          </v-btn>
          <v-btn color="red-darken-1" @click="confirmDelete">{{ $t('delete_thread_ok_text', 'Yes, delete it') }}</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <SelectAccounts :dialogVisible="isSelectAccountsVisible"></SelectAccounts>
  </v-container>
</template>

<script>
import {ref, onMounted, onBeforeUnmount} from 'vue';
import {useI18n} from 'vue-i18n';
import SelectAccounts from './../SocialMedia/SelectAccounts.vue'
export default {
  name: 'SubMenu',
  props: {
    userContextList: {
      type: Array,
      required: true,
      default: () => [],
    },

  },
  components:{SelectAccounts},
  setup(props) {
    const isComparisonOpen = ref(false);
    const deleteDialog = ref(false);
    const selectedBotResponses = ref([]);
    const {t} = useI18n();
    const isSelectAccountsVisible=ref(false)
    const toggleComparison = () => {
      isComparisonOpen.value = !isComparisonOpen.value;
      const eventName = isComparisonOpen.value ? 'comparison-open' : 'comparison-close';
      localStorage.setItem('isComparisonOpen', JSON.stringify(isComparisonOpen.value));
      const event = new CustomEvent(eventName, {});
      window.dispatchEvent(event);
    };

    const exportToExcel = () => {
      isComparisonOpen.value = !isComparisonOpen.value;
      const eventName = 'usercontext-export-excel'
      const event = new CustomEvent(eventName, {});
      window.dispatchEvent(event);
    };

    const onSelectedBotResponse = ((event) => {
      selectedBotResponses.value = event.detail.selectedItems
    });


    onMounted(() => {
      window.addEventListener('comparison-bot-response-selected', onSelectedBotResponse);
    });

    onBeforeUnmount(() => {
      window.removeEventListener('comparison-bot-response-selected', onSelectedBotResponse);
    });


    const openDeleteDialog = () => {
      deleteDialog.value = true;
    };

      const publishSocialMedia = () => {
      const event = new CustomEvent('socialmedia-accounts-selection-open', {detail: {}});
      window.dispatchEvent(event);
    };

    const cancelDelete = () => {
      deleteDialog.value = false;
      console.log(t('delete_thread_cancel_log', 'Deletion canceled'));
    };

    const confirmDelete = () => {
      deleteDialog.value = false;
      const event = new CustomEvent('delete-thread', {detail: {thread_id: props.userContextList[0].thread_id}});
      window.dispatchEvent(event);
    };

    onMounted(() => {
      const savedState = JSON.parse(localStorage.getItem('isComparisonOpen'));
      if (savedState !== null) {
        setTimeout(() => {
          const eventName = savedState ? 'comparison-open' : 'comparison-close';
          const event = new CustomEvent(eventName, {});
          window.dispatchEvent(event);
          isComparisonOpen.value = savedState;
        });
      }
    });

    return {
      isComparisonOpen,
      toggleComparison,
      deleteDialog,
      openDeleteDialog,
      cancelDelete,
      confirmDelete,
      exportToExcel,
      onSelectedBotResponse,
      publishSocialMedia,
      selectedBotResponses,
      isSelectAccountsVisible
    };
  },
};
</script>

<style scoped>
.panel-menu-button {
  margin: 5px;
}
</style>