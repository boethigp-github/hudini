<template>
  <a-menu mode="horizontal">
    <!-- Main Menu Item 1 with Icon -->
    <a-sub-menu key="1">
      <template #icon>
        <database-outlined />
      </template>
      <template #title>{{ t('model_responses', 'Model Responses') }}</template>

      <!-- Submenu Item 1 with Icon -->
      <a-menu-item key="1-1" @click="handleCompareClick">
        <template #icon>
          <setting-outlined />
        </template>
        {{ t('compare', 'Compare') }}
      </a-menu-item>
    </a-sub-menu>

    <!-- Main Menu Item 2 with Icon -->
    <a-sub-menu key="2">
      <template #icon>
        <form-outlined />
      </template>
      <template #title>{{ t('prompts', 'Prompts') }}</template>

      <!-- Submenu Item 2 with Icon -->
      <a-menu-item key="2-1" @click="handleSystemPromptsClick">
        <template #icon>
          <edit-outlined />
        </template>
        {{ t('system_prompts', 'System Prompts') }}
      </a-menu-item>
    </a-sub-menu>
  </a-menu>
</template>

<script>
import { useI18n } from 'vue-i18n';
import { Menu } from 'ant-design-vue';
import { DatabaseOutlined, FormOutlined, SettingOutlined, EditOutlined } from '@ant-design/icons-vue';

export default {
  name: 'ChatMenu',
  components: {
    'a-menu': Menu,
    'a-menu-item': Menu.Item,
    'a-sub-menu': Menu.SubMenu,
    'database-outlined': DatabaseOutlined,
    'form-outlined': FormOutlined,
    'setting-outlined': SettingOutlined,
    'edit-outlined': EditOutlined,
  },
  setup() {
    const { t } = useI18n();

    const handleCompareClick = () => {
      const event = new CustomEvent("comparison-open", {  });
      window.dispatchEvent(event);
    };

    const handleSystemPromptsClick = () => {
      console.log("System Prompts clicked");
    };

    return {
      t,
      handleCompareClick,
      handleSystemPromptsClick,
    };
  },
};
</script>

<style scoped>
 .ant-menu{
  background: none;
}
</style>
