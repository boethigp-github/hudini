<template>
  <a-menu
    title="comparison"
    size="small"
    id="response_panel_action"
    :inlineCollapsed="true"
    v-model:openKeys="openKeys"
    v-model:selectedKeys="selectedKeys"
  >
    <a-sub-menu size="small" key="sub1" @titleClick="titleClick">
      <template #icon>
        <TableOutlined />
      </template>
    </a-sub-menu>
  </a-menu>
</template>

<script>
import { ref } from 'vue';
import { TableOutlined } from '@ant-design/icons-vue';
import { Menu } from 'ant-design-vue';

export default {
  name: 'SubMenu',
  components: {
    TableOutlined,
    'a-menu': Menu,
    'a-sub-menu': Menu.SubMenu,
  },
  setup() {
    const openKeys = ref(['sub1']);
    const selectedKeys = ref(['1']);

    const titleClick = () => {
      const event = new CustomEvent("comparison-open", {});
      window.dispatchEvent(event);
    };

    return {
      openKeys,
      selectedKeys,
      titleClick,
    };
  },
};
</script>

<style scoped>
/* Optional: Füge hier spezifische Styles für das Submenü hinzu */
</style>
