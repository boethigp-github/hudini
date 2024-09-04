<template>
  <a-row>
    <a-col :span="23">
      <div id="response" class="response" ref="responseElement">
        <template v-for="(dialog, dialogIndex) in groupedResponses" :key="dialogIndex">
          <a-card dense size="small" :id="`dialog_${dialog.promptId}`" class="dialog-card">
            <a-list
                :data-source="dialog.items"
                :bordered="false"
                size="small"
            >
              <template #renderItem="{ item }">
                <a-list-item
                    size="small"
                    :rowKey="item.id"
                    :data-prompt-id="dialog.promptId"
                    @mouseover="handleMouseOver(dialog.promptId)"
                    @mouseout="handleMouseOut(dialog.promptId)"
                    :class="[item.status === 'complete' ? 'response-item' : 'incomplete-item', 'fade-in']"
                >
                  <template #actions>
                    <span v-for="{ icon, text } in actions" :key="icon">
                      <component :is="icon" style="margin-right: 8px"/>
                      {{ text }}
                    </span>
                  </template>

                  <a-list-item-meta :class="[item.type, { highlighted: isHighlighted(dialog.promptId) }]">
                    <template #avatar>
                      <user-outlined v-if="item.type === 'user'" class="user-icon"/>
                      <robot-outlined v-else class="bot-icon"/>
                    </template>
                    <template #title>
                      <div v-if="item.type === 'user'" class="user-content">
                        <span class="prompt-text">{{ item.content }}</span>
                      </div>
                      <div v-else class="response-metadata">
                        <span class="model">{{ $t('model') }}: {{ item.model }}</span>
                        <span class="timestamp">{{ formatTimestamp(item.timestamp) }}</span>
                        <span class="timestamp">{{ $t('prompt_tokens', 'Prompt Tokens') }}: {{
                            item.rawData?.completion?.usage.prompt_tokens
                          }}</span>
                        <span class="timestamp">{{ $t('completion_tokens', 'Completion Tokens') }}: {{
                            item.rawData?.completion?.usage.completion_tokens
                          }}</span>
                        <span class="timestamp">{{ $t('total_tokens', 'All Tokens') }}: {{
                            item.rawData?.completion?.usage.total_tokens
                          }}</span>
                        <span class="timestamp">{{ $t('run_time', 'Run time') }}: {{

                            formatDuration(item.rawData?.completion?.usage.started, item.rawData?.completion?.usage.ended)
                          }}</span>
                      </div>
                    </template>
                    <template #description>
                      <template v-if="item.type === 'bot'">
                        <VueMarkdownIT
                            v-if="!item.error"
                            class="bot-answer-md"
                            :breaks="true"
                            :plugins="plugins"
                            :source="item.content"
                        />
                        <span v-else class="error-message">{{ item.error }}</span>
                      </template>
                    </template>
                  </a-list-item-meta>
                </a-list-item>
              </template>
            </a-list>
          </a-card>
        </template>
        <ComparisonDrawer :plugins="plugins" :comparisonData="comparisonData" width="90%"/>
      </div>
    </a-col>

    <a-col :span="1" class="nav-container">
      <ResponsePanelMenu/>
    </a-col>
  </a-row>
</template>

<script>
import {nextTick, watch, ref, onMounted, computed} from 'vue';
import {
  UserOutlined,
  RobotOutlined,
  TableOutlined,
  StarOutlined,
  LikeOutlined,
  MessageOutlined
} from '@ant-design/icons-vue';
import {Button, Skeleton, Row, Col, Menu, List, Card} from 'ant-design-vue';
import MarkdownIt from 'markdown-it';
import MarkdownItHighlightJs from 'markdown-it-highlightjs';
import MarkdownItStrikethroughAlt from 'markdown-it-strikethrough-alt';
import MarkdownItAbbr from 'markdown-it-abbr';
import MarkdownItAnchor from 'markdown-it-anchor';
import MarkdownItDefList from 'markdown-it-deflist';
import MarkdownItFootnote from 'markdown-it-footnote';
import MarkdownItIns from 'markdown-it-ins';
import MarkdownSub from 'markdown-it-sub';
import MarkdownSup from 'markdown-it-sup';
import MarkdownTaskList from 'markdown-it-task-lists';
import MarkdownMark from 'markdown-it-mark';
import MarkdownCollapsible from 'markdown-it-collapsible';
import MarkdownCheckbox from 'markdown-it-checkbox';
import MarkdownTocDoneRight from 'markdown-it-toc-done-right';
import Markdown from 'vue3-markdown-it';
import './ResponsePanel/Highlite.css';
import ComparisonDrawer from './ResponsePanel/ComparisonDrawer.vue';
import './ResponsePanel/response_panel.css';
import ResponsePanelMenu from './ResponsePanel/ResponsePanelMenu.vue'

export default {
  name: 'ResponsePanel',
  components: {
    UserOutlined,
    RobotOutlined,
    TableOutlined,
    StarOutlined,
    LikeOutlined,
    MessageOutlined,
    MarkdownCollapsible,
    MarkdownCheckbox,
    VueMarkdownIT: Markdown,
    'a-button': Button,
    'a-skeleton': Skeleton,
    'a-row': Row,
    'a-col': Col,
    'a-menu': Menu,
    'a-sub-menu': Menu.SubMenu,
    'a-list': List,
    'a-list-item': List.Item,
    'a-list-item-meta': List.Item.Meta,
    'a-card': Card,
    ComparisonDrawer,
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
    const openKeys = ref(['sub1']);
    const selectedKeys = ref(['1']);
    const highlightedPromptId = ref(null);

    const actions = [
      {icon: StarOutlined, text: '156'},
      {icon: LikeOutlined, text: '156'},
      {icon: MessageOutlined, text: '2'},
    ];

    const groupedResponses = computed(() => {
      const groups = [];
      let currentGroup = null;
      props.responses.forEach(response => {
        if (response.prompt) {
          if (currentGroup) {
            groups.push(currentGroup);
          }
          currentGroup = {
            promptId: response.prompt_id,
            items: [{
              id: response.prompt_id,
              type: 'user',
              content: response.prompt,
              status: response.status,
              rawData: response
            }]
          };
        } else if (currentGroup) {
          currentGroup.items.push({
            id: response.prompt_id + '-response',
            type: 'bot',
            content: response.completion?.choices[0].message.content,
            model: response.model,
            timestamp: response.completion?.created,
            error: response.error,
            status: response.status,
            rawData: response
          });
        }
      });

      if (currentGroup) {
        groups.push(currentGroup);
      }

      // Reverse the order of groups but keep prompt first and responses after
      return groups.reverse();
    });


    const formatDuration = (start, end) => {
      const duration = end - start;
      const seconds = ((duration % 60000)).toFixed(0);
      return `${seconds} ms`;
    };

    const isHighlighted = (prompt_id) => {
      return prompt_id === highlightedPromptId.value;
    };

    const handleMouseOver = (prompt_id) => {
      highlightedPromptId.value = prompt_id;
    };

    const handleMouseOut = (prompt_id) => {
      highlightedPromptId.value = null;
    };

    const handleEdit = (item) => {
      // Implement edit functionality
      console.log('Edit item:', item);
    };

    const handleMore = (item) => {
      // Implement more functionality
      console.log('More details for item:', item);
    };

    const scrollToBottom = () => {
      nextTick(() => {
        if (responseElement.value) {
          responseElement.value.scrollTop = responseElement.value.scrollHeight;
        }
      });
    };

    const plugins = [
      {plugin: MarkdownItHighlightJs},
      {plugin: MarkdownItStrikethroughAlt},
      {plugin: MarkdownIt},
      {plugin: MarkdownItAbbr},
      {plugin: MarkdownItAnchor},
      {plugin: MarkdownItDefList},
      {plugin: MarkdownItFootnote},
      {plugin: MarkdownItIns},
      {plugin: MarkdownSub},
      {plugin: MarkdownSup},
      {plugin: MarkdownTaskList},
      {plugin: MarkdownTocDoneRight},
      {plugin: MarkdownMark},
      {plugin: MarkdownCollapsible},
      {plugin: MarkdownCheckbox},
    ];

    const formatTimestamp = timestamp => {
      if (!timestamp) return '';
      const date = new Date(timestamp * 1000);
      return date.toLocaleString();
    };

    // Prepare comparison data
    const comparisonData = computed(() => {
      return groupedResponses.value.flatMap(group =>
          group.items.map(item => ({
            model: item.type === 'user' ? 'UserPrompt' : item.model || 'Unknown',
            content: item.content || '',
            timestamp: item.timestamp ? formatTimestamp(item.timestamp) : '',
            error: item.error || '',
            rawData: item.rawData
          }))
      );
    });
    watch(
        () => props.responses,
        () => {
          scrollToBottom();
        },
        {deep: true}
    );

    onMounted(() => {
      // Any mounting logic if needed
    });

    return {
      responseElement,
      groupedResponses,
      actions,
      plugins,
      comparisonData,
      openKeys,
      selectedKeys,
      handleMouseOver,
      handleMouseOut,
      isHighlighted,
      handleEdit,
      handleMore,
      formatDuration,
      scrollToBottom,
      formatTimestamp,

    };
  },
};
</script>

<style scoped>
.user-prompt :deep(.ant-list-item-meta-content) {
  background-color: #d9d9d9; /* Darker grey for user prompts */
  border-radius: 12px;
  padding: 10px;
  text-align: right;
}

.bot-response :deep(.ant-list-item-meta-content) {
  background-color: #f0f0f0; /* Lighter grey for bot responses */
  border-radius: 12px;
  padding: 10px;

}

/* Adjustments for list items */
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

/* Styling for the prompt text and bot response content */
.prompt-text, :deep(.ant-list-item-meta-description) {
  word-break: break-word;
}

/* Adjust avatar positioning */
:deep(.ant-list-item-meta-avatar) {
  align-self: flex-start;
  margin-top: 8px;
}

/* Action icons styling */
:deep(.ant-list-item-action) {
  margin-top: 8px;
}

:deep(.ant-list-item-action > li) {
  padding: 0 8px;
  cursor: pointer;
}

:deep(.ant-list-item-action > li:hover) {
  color: #1890ff;
}
</style>
