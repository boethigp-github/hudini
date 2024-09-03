<template>
  <a-menu
    title="comparison"
    size="small"
    id="response_panel_action"
    :inlineCollapsed="true"
    v-model:openKeys="openKeys"
    v-model:selectedKeys="selectedKeys"
  >
    <a-menu-item size="small"  :title="$t('comparison_view', 'Comparison view')" key="sub1" @click="openComparison">
      <template #icon>
        <TableOutlined />
      </template>
    </a-menu-item>

    <a-menu-item size="small" :title="$t('delete_thread', 'Delete thread')" key="delete_thread" @click="deleteThread">
      <template #icon>
        <DeleteOutlined />
      </template>
    </a-menu-item>
  </a-menu>
</template>

<script>
import { ref } from 'vue';
import { TableOutlined, DeleteOutlined } from '@ant-design/icons-vue';
import { Menu } from 'ant-design-vue';

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


    const openComparison = () => {
      const event = new CustomEvent('comparison-open', {});
      window.dispatchEvent(event);
    };

    const deleteThread = () => {
      const event = new CustomEvent('delete-thread', {
        detail: { },
      });
      window.dispatchEvent(event);
    };

    return {
      openKeys,
      selectedKeys,
      openComparison,
      deleteThread,
    };
  },
};
</script>

<style scoped>
/* Optional: Add specific styles for the submenu here */
</style>
