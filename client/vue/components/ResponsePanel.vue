<template>
  <div id="response" class="response" ref="responseElement">
    <div v-for="(item, index) in responses"
         :key="index"
         :class="[item.status === 'complete' ? 'response-item' : 'incomplete-item', 'fade-in']"
    >
      <div v-if="item.prompt" class="user-prompt fade-in">
        <user-outlined class="user-icon"/>
        <span class="prompt-text">{{ item.prompt }}</span>
      </div>

      <div v-if="item.completion?.choices?.length" class="bot-response fade-in">
        <robot-outlined class="bot-icon"/>
        <div class="response-content">
          <div class="response-metadata">
            <span class="model">{{ $t('model') }}: {{ item.model }}</span><br>
            <span class="timestamp">{{ formatTimestamp(item.completion.created) }}</span>
          </div>

          <VueMarkdownIT :breaks="true" :plugins="plugins" :source="item.completion.choices[0].message.content"/>
        </div>
      </div>
      <div v-else-if="item.error" class="bot-response fade-in">
        <robot-outlined class="bot-icon"/>
        <div class="response-content">
          <div class="response-metadata" v-if="item.model">
            <span class="model">{{ $t('model') }}: {{ item.model }}</span>
          </div>
          <div>
            {{ item.error }}
          </div>
        </div>
      </div>
    </div>
    <a-skeleton :loading="loading" active :paragraph="{ rows: 2 }" style="margin-bottom: 10px"></a-skeleton>

    <!-- Compare Button -->
    <a-button type="primary" @click="showDrawer">Compare</a-button>

    <!-- Comparison Drawer Component -->
    <ComparisonDrawer :plugins="plugins" :visible="drawerVisible" :comparisonData="comparisonData" width="90%" @close="drawerVisible = false" />
  </div>
</template>

<script>
import { nextTick, watch, ref, onMounted, computed } from 'vue';
import { UserOutlined, RobotOutlined } from '@ant-design/icons-vue';
import { Button, Skeleton } from 'ant-design-vue';
import MarkdownIt from 'markdown-it';
import MarkdownItHighlightJs from 'markdown-it-highlightjs';
import MarkdownItStrikethroughAlt from 'markdown-it-strikethrough-alt';
import MarkdownItAbbr from 'markdown-it-abbr';
import MarkdownItAncor from 'markdown-it-anchor';
import MarkdownItDefList from 'markdown-it-deflist';
import MarkdownItFootnote from 'markdown-it-footnote';
import MarkdownItIn from 'markdown-it-ins';
import MarkdownSub from 'markdown-it-sub';
import MarkdownSup from 'markdown-it-sup';
import MarkdownTaskList from 'markdown-it-task-lists';
import MarkdownMark from 'markdown-it-mark';
import MarkdownTocDoneRight from 'markdown-it-toc-done-right';
import Markdown from 'vue3-markdown-it';
import './ResponsePanel/Highlite.css';
import ComparisonDrawer from './ResponsePanel/ComparisonDrawer.vue';

export default {
  name: 'ResponsePanel',
  components: {
    UserOutlined,
    RobotOutlined,
    VueMarkdownIT: Markdown,
    'a-button': Button,
    'a-skeleton': Skeleton,
    ComparisonDrawer,
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
    const drawerVisible = ref(false);

    const scrollToBottom = () => {
      nextTick(() => {
        if (responseElement.value) {
          responseElement.value.scrollTop = responseElement.value.scrollHeight;
        }
      });
    };

    const showDrawer = () => {
      drawerVisible.value = true;
    };

    const plugins = [
      { plugin: MarkdownItHighlightJs },
      { plugin: MarkdownItStrikethroughAlt },
      { plugin: MarkdownIt },
      { plugin: MarkdownItAbbr },
      { plugin: MarkdownItAncor },
      { plugin: MarkdownItDefList },
      { plugin: MarkdownItFootnote },
      { plugin: MarkdownItIn },
      { plugin: MarkdownSub },
      { plugin: MarkdownSup },
      { plugin: MarkdownTaskList },
      { plugin: MarkdownTocDoneRight },
      { plugin: MarkdownMark },
    ];

    const formatTimestamp = (timestamp) => {
      const date = new Date(timestamp * 1000);
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      const hours = String(date.getHours()).padStart(2, '0');
      const minutes = String(date.getMinutes()).padStart(2, '0');
      const seconds = String(date.getSeconds()).padStart(2, '0');
      return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
    };

    // Prepare comparison data
    const comparisonData = computed(() => {
      return props.responses.map((response) => ({
        model: response.model,
        content: response.completion?.choices[0].message.content || 'No content',
        timestamp: formatTimestamp(response.completion?.created),
        error: response.error || 'No error',
      }));
    });

    watch(
        () => props.responses,
        () => {
          scrollToBottom();
        },
        { deep: true }
    );

    onMounted(() => {});

    return {
      responseElement,
      scrollToBottom,
      formatTimestamp,
      plugins,
      showDrawer,
      drawerVisible,
      comparisonData,
    };
  },
};
</script>



<style scoped>
.response {
  max-height: 68vh;
  height: 68vh;
  overflow-y: auto;
  padding: 5px;
  margin: 0;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background-color: #ffffff;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.response-item, .user-prompt, .bot-response {
  border: none;
  border-radius: 12px;
  padding: 5px;
  margin-top: 12px;
  font-size: 16px;
  line-height: 1.5;
  opacity: 0;
  transition: opacity 0.2s ease-in-out;
  display: flex;
  align-items: flex-start;
}

.user-prompt {
  background: #e8e8e8;
  float: right;
  max-width: 80%;
  margin-left: auto;
}

.bot-response {
  background: #f5f5f5;
  float: left;
  max-width: 100%;
}

.user-icon, .bot-icon {
  margin-right: 8px;
  font-size: 18px;
  flex-shrink: 0;
}

.user-icon {
  color: #1890ff;
}

.bot-icon {
  color: #52c41a;
}

.prompt-text, .response-content {
  flex: 1;
}

.fade-in {
  animation: fadeIn 0.2s ease-in-out forwards;
  animation-delay: 0.1s;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.response-metadata {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  color: #555;
  font-size: 14px;
}

.timestamp {
  font-size: 13px;
  color: #777;
}

.model {
  color: #444;
  font-weight: 600;
  margin-top: -5px;
}

.placeholder {
  color: #999;
  font-style: italic;
  font-size: 16px;
}

/* Styles for syntax highlighting */
:deep(pre[class*="language-"]) {
  padding: 1em;
  margin: .5em 0;
  overflow: auto;
  border-radius: 0.3em;
}

:deep(code[class*="language-"]) {
  background: none;
  font-family: Consolas, Monaco, 'Andale Mono', 'Ubuntu Mono', monospace;
  text-align: left;
  white-space: pre;
  word-spacing: normal;
  word-break: normal;
  word-wrap: normal;
  line-height: 1.5;
  tab-size: 4;
  hyphens: none;
}

/* You may want to adjust these global styles or move them to a global stylesheet */
body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  line-height: 1.6;
  color: #333;
}

h1, h2, h3, h4, h5, h6 {
  font-family: 'Arial', sans-serif;
  margin-top: 1.5em;
  margin-bottom: 0.5em;
}

p {
  margin-bottom: 1em;
}

code {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  background-color: #000;
  padding: 2px 4px;
  border-radius: 4px;
}

.hljs  {
  background: yellow;
  font-family: Consolas, Monaco, 'Andale Mono', 'Ubuntu Mono', monospace;
  text-align: left;
  white-space: pre;
  word-spacing: normal;
  word-break: normal;
  word-wrap: normal;
  line-height: 1.5;
  tab-size: 4;
  hyphens: none;

}


</style>