<template>
  <v-container class="panel-menu">
    <v-row>
      <v-btn class="panel-menu-button" icon="mdi-select-compare" :title="$t('comparison_view', 'Comparison view')" key="sub1"
             @click="openComparison"></v-btn>
    </v-row>
    <v-row>
      <v-btn   class="panel-menu-button" icon="mdi-delete-circle" :title="$t('delete_thread', 'Delete thread')" key="delete_thread"
             @click="confirmDeleteThread"></v-btn>
    </v-row>
  </v-container>
</template>

<script>
import {ref} from 'vue';

import {useI18n} from 'vue-i18n';

export default {
  name: 'SubMenu',
  components: {
  },
  setup() {
    const openKeys = ref(['sub1']);
    const selectedKeys = ref(['1']);
    const {t} = useI18n();

    const openComparison = () => {
      const event = new CustomEvent('comparison-open', {});
      window.dispatchEvent(event);
    };

    const deleteThread = () => {
      const event = new CustomEvent('delete-thread', {
        detail: {},
      });
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

    return {
      openKeys,
      selectedKeys,
      openComparison,
      confirmDeleteThread,
    };
  },
};
</script>

<style scoped>
.panel-menu-button{
  margin: 5px;
}


</style>
