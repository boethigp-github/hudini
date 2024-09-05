<template>
  <a-list-item
    size="small"
    :class="[
      response.status === 'complete' ? 'response-item' : 'incomplete-item',
      'bot-response', 'fade-in',
      { 'float-left': hasMultipleResponses }
    ]"
    @mouseover="$emit('mouseover', response.prompt_id)"
    @mouseout="$emit('mouseout', response.prompt_id)">
    <template #actions>
      <span v-for="{ icon, text } in actions" :key="icon">
        <component :is="icon" style="margin-right: 8px"/>
        {{ text }}
      </span>
    </template>

    <a-list-item-meta :class="{ highlighted: isHighlighted }">
      <template #avatar>
        <robot-outlined class="bot-icon"/>
      </template>
      <template #title>
        <div class="response-metadata">
          <span class="model">{{ response.model }}</span>
          <span class="timestamp">{{ formatTimestamp(response.completion?.created) }}</span>
          <span class="timestamp">{{ $t('prompt_tokens', 'Prompt Tokens') }}: {{ response.completion?.usage.prompt_tokens }}</span>
          <span class="timestamp">{{ $t('completion_tokens', 'Completion Tokens') }}: {{ response.completion?.usage.completion_tokens }}</span>
          <span class="timestamp">{{ $t('total_tokens', 'All Tokens') }}: {{ response.completion?.usage.total_tokens }}</span>
          <span class="timestamp">{{ $t('run_time', 'Run time') }}: {{ formatDuration(response.completion?.usage.started, response.completion?.usage.ended) }}</span>
        </div>
      </template>
      <template #description>
        <VueMarkdownIT
          v-if="!response.error"
          class="bot-answer-md"
          :breaks="true"
          :plugins="plugins"
          :source="response.completion?.choices[0].message.content"/>
        <span v-else class="error-message">{{ response.error }}</span>
      </template>
    </a-list-item-meta>
  </a-list-item>
</template>

<script>
import { RobotOutlined, StarOutlined, LikeOutlined, MessageOutlined } from '@ant-design/icons-vue';
import { List } from 'ant-design-vue';
import Markdown from 'vue3-markdown-it';
import { markdownPlugins } from './../../stores/markdownPlugins.js';

import './Highlite.css';

export default {
  name: 'BotResponse',
  components: {
    RobotOutlined,
    StarOutlined,
    LikeOutlined,
    MessageOutlined,
    VueMarkdownIT: Markdown,
    'a-list-item': List.Item,
    'a-list-item-meta': List.Item.Meta,
  },
  props: {
    response: {
      type: Object,
      required: true,
    },
    isHighlighted: {
      type: Boolean,
      default: false,
    },
    hasMultipleResponses: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['mouseover', 'mouseout'],
  setup() {
    const actions = [
      {icon: StarOutlined, text: '156'},
      {icon: LikeOutlined, text: '156'},
      {icon: MessageOutlined, text: '2'},
    ];

    const formatDuration = (start, end) => {
      const duration = end - start;
      const seconds = ((duration % 60000) / 1000).toFixed(2);
      return `${seconds} s`;
    };

    const formatTimestamp = timestamp => {
      if (!timestamp) return '';
      const date = new Date(timestamp * 1000);
      return date.toLocaleString();
    };

    return {
      actions,
      plugins: markdownPlugins,
      formatDuration,
      formatTimestamp,
    };
  },
};
</script>

<style scoped>
.bot-response :deep(.ant-list-item-meta-content) {
  background-color: #f0f0f0;
  border-radius: 12px;
  padding: 10px;
}

.bot-response.float-left :deep(.ant-list-item-meta-content) {
  text-align: left;
}

:deep(.ant-list-item-meta-description) {
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