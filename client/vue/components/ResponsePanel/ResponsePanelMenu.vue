<template>
  <v-container class="panel-menu">
    <v-row>

      11: {{isComparisonOpen}}
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
        @click="confirmDeleteThread"
      ></v-btn>
    </v-row>
  </v-container>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';

export default {
  name: 'SubMenu',
  setup() {
    const isComparisonOpen = ref(false);
    const { t } = useI18n();
    const toggleComparison = () => {
      isComparisonOpen.value = !isComparisonOpen.value;
      const eventName = isComparisonOpen.value ? 'comparison-open' : 'comparison-close';
      localStorage.setItem('isComparisonOpen', JSON.stringify( isComparisonOpen.value));
      const event = new CustomEvent(eventName, {});
      window.dispatchEvent(event);
    };

    // Delete Thread Function
    const deleteThread = () => {
      const event = new CustomEvent('delete-thread', { detail: {} });
      window.dispatchEvent(event);
    };


    const confirmDeleteThread = () => {
      Modal.confirm({
        title: t('delete_thread_confirmation_title', 'Are you sure you want to delete this thread?'),
        content: t('delete_thread_confirmation_content', 'This action cannot be undone.'),
        okText: t('delete_thread_ok_text', 'Yes, delete it'),
        okType: 'danger',
        cancelText: t('delete_thread_cancel_text', 'No, keep it'),
        onOk() {
          deleteThread();
        },
        onCancel() {
          console.log(t('delete_thread_cancel_log', 'Deletion canceled'));
        },
      });
    };

    // Load state from local storage on mount and throw corresponding event
    onMounted(() => {
      const savedState = JSON.parse(localStorage.getItem('isComparisonOpen'));
      if (savedState !== null) {
        setTimeout(()=>{
        const eventName = savedState ? 'comparison-open' : 'comparison-close';
        const event = new CustomEvent(eventName, {});
        window.dispatchEvent(event);
        isComparisonOpen.value = savedState
        })
      }
    });

    return {
      isComparisonOpen,
      toggleComparison,
      confirmDeleteThread,
    };
  },
};
</script>

<style scoped>
.panel-menu-button {
  margin: 5px;
}
</style>
