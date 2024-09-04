<template>
  <a-row>
    <a-col :span="23">
      <div id="response" class="response" ref="responseElement">
        <template v-for="(response, index) in responses.slice().reverse()" :key="index">
          <a-card dense size="small" :id="`dialog_${response.prompt_id}`" class="dialog-card">
            <a-list
              :data-source="[response]"
              :bordered="false"
              size="small"
            >
              <template #renderItem="{ item }">
                <!-- User Prompt -->
                <a-list-item v-if="item.prompt"
                  size="small"
                  :rowKey="item.prompt_id"
                  :class="['user-prompt', 'fade-in']"
                  @mouseover="handleMouseOver(item.prompt_id)"
                  @mouseout="handleMouseOut(item.prompt_id)">
                  <a-list-item-meta :class="{ highlighted: isHighlighted(item.prompt_id) }">
                    <template #avatar>
                      <user-outlined class="user-icon"/>
                    </template>
                    <template #title>
                      <div class="user-content">
                        <span class="prompt-text">{{ item.prompt }}</span>
                      </div>
                    </template>
                  </a-list-item-meta>
                </a-list-item>

                <!-- Bot Response -->
                <a-list-item
                  size="small"
                  v-if="item.completion"
                  :rowKey="`${item.prompt_id}-response`"
                  :class="[item.status === 'complete' ? 'response-item' : 'incomplete-item', 'bot-response', 'fade-in']"
                  @mouseover="handleMouseOver(item.prompt_id)"
                  @mouseout="handleMouseOut(item.prompt_id)">
                  <template #actions>
                    <span v-for="{ icon, text } in actions" :key="icon">
                      <component :is="icon" style="margin-right: 8px"/>
                      {{ text }}
                    </span>
                  </template>

                  <a-list-item-meta :class="{ highlighted: isHighlighted(item.prompt_id) }">
                    <template #avatar>
                      <robot-outlined class="bot-icon"/>
                    </template>
                    <template #title>
                      <div class="response-metadata">
                        <span class="model">{{ item.model }}</span>
                        <span class="timestamp">{{ formatTimestamp(item.completion?.created) }}</span>
                        <span class="timestamp">{{ $t('prompt_tokens', 'Prompt Tokens') }}: {{ item.completion?.usage.prompt_tokens }}</span>
                        <span class="timestamp">{{ $t('completion_tokens', 'Completion Tokens') }}: {{ item.completion?.usage.completion_tokens }}</span>
                        <span class="timestamp">{{ $t('total_tokens', 'All Tokens') }}: {{ item.completion?.usage.total_tokens }}</span>
                        <span class="timestamp">{{ $t('run_time', 'Run time') }}: {{ formatDuration(item.completion?.usage.started, item.completion?.usage.ended) }}</span>
                      </div>
                    </template>
                    <template #description>
                      <VueMarkdownIT
                        v-if="!item.error"
                        class="bot-answer-md"
                        :breaks="true"
                        :plugins="plugins"
                        :source="item.completion?.choices[0].message.content"/>
                      <span v-else class="error-message">{{ item.error }}</span>
                    </template>
                  </a-list-item-meta>
                </a-list-item>
              </template>
            </a-list>
          </a-card>
        </template>
      </div>
      <ComparisonDrawer :plugins="plugins" :responses="responses" width="90%"/>
    </a-col>

    <a-col :span="1" class="nav-container">
      <ResponsePanelMenu/>
    </a-col>
  </a-row>
</template>

<script>
import {nextTick, watch, ref, onMounted} from 'vue';
import {
  UserOutlined,
  RobotOutlined,
  StarOutlined,
  LikeOutlined,
  MessageOutlined
} from '@ant-design/icons-vue';
import {Row, Col, List, Card} from 'ant-design-vue';
import Markdown from 'vue3-markdown-it';
import './ResponsePanel/Highlite.css';
import './ResponsePanel/response_panel.css';
import ResponsePanelMenu from './ResponsePanel/ResponsePanelMenu.vue';
import {markdownPlugins} from './../stores/markdownPlugins.js';  // Assume this is defined elsewhere
import ComparisonDrawer from './ResponsePanel/ComparisonDrawer.vue';  // Assume this is defined elsewhere

export default {
  name: 'ResponsePanel',
  components: {
    UserOutlined,
    RobotOutlined,
    StarOutlined,
    LikeOutlined,
    MessageOutlined,
    ComparisonDrawer,
    VueMarkdownIT: Markdown,
    'a-row': Row,
    'a-col': Col,
    'a-list': List,
    'a-list-item': List.Item,
    'a-list-item-meta': List.Item.Meta,
    'a-card': Card,
    ResponsePanelMenu
  },
  props: {
    responses: {
      type: Array,
      required: true,
      default: () => [],
    },
    loading: {
      type: Boolean,
      required: true,
      default: false,
    },
  },
  setup(props) {
    const responseElement = ref(null);
    const highlightedPromptId = ref(null);

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

    const isHighlighted = (prompt_id) => {
      return prompt_id === highlightedPromptId.value;
    };

    const handleMouseOver = (prompt_id) => {
      highlightedPromptId.value = prompt_id;
    };

    const handleMouseOut = () => {
      highlightedPromptId.value = null;
    };

    const scrollToBottom = () => {
      nextTick(() => {
        if (responseElement.value) {
          responseElement.value.scrollTop = responseElement.value.scrollHeight;
        }
      });
    };

    const formatTimestamp = timestamp => {
      if (!timestamp) return '';
      const date = new Date(timestamp * 1000);
      return date.toLocaleString();
    };

    watch(
        () => props.responses,
        () => {
          scrollToBottom();
        },
        {deep: true}
    );

    onMounted(() => {
      scrollToBottom();
    });

    return {
      responseElement,
      actions,
      plugins: markdownPlugins,
      handleMouseOver,
      handleMouseOut,
      isHighlighted,
      formatDuration,
      scrollToBottom,
      formatTimestamp,
    };
  },
};
</script>

<style scoped>
.user-prompt :deep(.ant-list-item-meta-content) {
  background-color: #d9d9d9;
  border-radius: 12px;
  padding: 10px;
  text-align: right;
}

.bot-response :deep(.ant-list-item-meta-content) {
  background-color: #f0f0f0;
  border-radius: 12px;
  padding: 10px;
}

:deep(.ant-list-item) {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  font-family: 'Georgia', Tahoma, Geneva, Verdana, sans-serif;
}

:deep(.ant-card-body) {
  padding: 5px;
}

:deep(.ant-list-item-meta) {
  width: 100%;
}

.prompt-text, :deep(.ant-list-item-meta-description) {
  word-break: break-word;
}

:deep(.ant-list-item-meta-avatar) {
  align-self: flex-start;
  margin-top: 8px;
}

:deep(.ant-list-item-action) {
  margin-top: 8px;
}

:deep(.ant-list-item-action > li) {
  padding: 0 8px;
  cursor: pointer;
}



.fade-in {
  animation: fadeIn 0.5s;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}


</style>