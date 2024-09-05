<template>
  <a-list-item
    size="small"
    :class="['user-prompt', 'fade-in']"
    @mouseover="$emit('mouseover', prompt.prompt_id)"
    @mouseout="$emit('mouseout', prompt.prompt_id)">
    <a-list-item-meta :class="{ highlighted: isHighlighted }">
      <template #avatar>
        <user-outlined class="user-icon"/>
      </template>
      <template #title>
        <div class="user-content">
          <span class="prompt-text">{{ prompt.prompt }}</span>
        </div>
      </template>
    </a-list-item-meta>
  </a-list-item>
</template>

<script>
import { UserOutlined } from '@ant-design/icons-vue';
import { List } from 'ant-design-vue';

export default {
  name: 'UserPrompt',
  components: {
    UserOutlined,
    'a-list-item': List.Item,
    'a-list-item-meta': List.Item.Meta,
  },
  props: {
    prompt: {
      type: Object,
      required: true,
    },
    isHighlighted: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['mouseover', 'mouseout'],
};
</script>

<style scoped>
.user-prompt :deep(.ant-list-item-meta-content) {
  background-color: #d9d9d9;
  border-radius: 12px;
  padding: 10px;
  text-align: right;
}

.prompt-text {
  word-break: break-word;
}

.fade-in {
  animation: fadeIn 0.5s;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
</style>