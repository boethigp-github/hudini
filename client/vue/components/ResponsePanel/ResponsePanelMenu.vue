<template>
  <a-menu
    title="comparison"
    size="small"
    id="response_panel_action"
    :inlineCollapsed="true"
    v-model:openKeys="openKeys"
    v-model:selectedKeys="selectedKeys"
  >
    <a-menu-item size="small" :title="$t('comparison_view', 'Comparison view')" key="sub1" @click="openComparison">
      <template #icon>
        <TableOutlined />
      </template>
    </a-menu-item>

    <a-menu-item size="small" :title="$t('delete_thread', 'Delete thread')" key="delete_thread" @click="confirmDeleteThread">
      <template #icon>
        <DeleteOutlined />
      </template>
    </a-menu-item>
  </a-menu>
</template>

<script>
import { ref } from 'vue';
import { TableOutlined, DeleteOutlined } from '@ant-design/icons-vue';
import { Menu, Modal } from 'ant-design-vue';
import { useI18n } from 'vue-i18n';
export default {
  name: 'SubMenu',
  components: {
    TableOutlined,
    DeleteOutlined,
    'a-menu': Menu,
    'a-sub-menu': Menu.SubMenu,
    'a-menu-item': Menu.Item,
  },
  setup() {
    const openKeys = ref(['sub1']);
    const selectedKeys = ref(['1']);
    const { t } = useI18n();

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
.ant-layout {
    display: flex;
    flex: auto;
    flex-direction: column;
    color: rgba(0, 0, 0, 0.88);
    min-height: 0;
    background: none;
    border: 1px solid red;
}
</style>
