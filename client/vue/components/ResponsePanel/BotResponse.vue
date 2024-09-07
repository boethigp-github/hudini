<template>
  <div :class="['response-item','bot-response', 'fade-in']"
       @mouseover="$emit('mouseover', contextDataItem.id)"
       @mouseout="$emit('mouseout', contextDataItem.id)">
    <div class="response-metadata">
      <span class="model"><robot-outlined class="bot-icon"/>{{ getModel() }}</span>
      <span class="timestamp">{{ getPromptTokens() }}</span>
      <span class="timestamp">{{ getCompletionTokens() }}</span>
      <span class="timestamp">{{ getTotalTokens() }}</span>
      <span class="timestamp">{{ getRunTime() }}</span>
    </div>
    <VueMarkdownIT
        class="bot-answer-md"
        :breaks="true"
        :plugins="getPlugins()"
        :source="contextDataItem?.completion?.choices[0].message.content"
    />
<!--    <span v-for="action in actions" :key="action.icon">-->
<!--      <component :is="action.icon" style="margin-right: 8px"/>-->
<!--      {{ action.text }}-->
<!--    </span>-->
  </div>
</template>

<script>
import {RobotOutlined, StarOutlined, LikeOutlined, MessageOutlined} from '@ant-design/icons-vue';
import Markdown from 'vue3-markdown-it';
import {markdownPlugins} from './../../stores/markdownPlugins.js';

export default {
  name: 'BotResponse',
  components: {
    RobotOutlined,
    StarOutlined,
    LikeOutlined,
    MessageOutlined,
    VueMarkdownIT: Markdown,
  },
  props: {
    contextDataItem: {
      type: Object,
      required: true,
    },
  },
  setup(props) {
    // Definiere actions-Liste korrekt in setup()
    const actions = [
      {icon: StarOutlined, text: '156'},
      {icon: LikeOutlined, text: '156'},
      {icon: MessageOutlined, text: '2'},
    ];

    // Eigene Methode für das Model
    const getModel = () => {
      return `Model: ${props.contextDataItem.completion?.model}`;
    };

    // Eigene Methode für Prompt Tokens
    const getPromptTokens = () => {
      return `Prompt Tokens: ${props.contextDataItem.completion?.usage?.prompt_tokens}`;
    };

    // Eigene Methode für Completion Tokens
    const getCompletionTokens = () => {
      return `Completion Tokens: ${props.contextDataItem.completion?.usage?.completion_tokens}`;
    };

    // Eigene Methode für Total Tokens
    const getTotalTokens = () => {
      return `Total Tokens: ${props.contextDataItem.completion?.usage?.total_tokens}`;
    };

    // Eigene Methode für die Laufzeit
    const getRunTime = () => {
      const start = props.contextDataItem.completion?.usage?.started;
      const end = props.contextDataItem.completion?.usage?.ended;
      const duration = end - start;
      const seconds = ((duration % 60000) / 1000).toFixed(2);
      return `Run Time: ${seconds} s`;
    };

    // Funktion, um Plugins zu holen
    const getPlugins = () => markdownPlugins;

    return {
      actions,
      getModel,
      getPromptTokens,
      getCompletionTokens,
      getTotalTokens,
      getRunTime,
      getPlugins,
    };
  },
};
</script>

<style scoped>


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

.bot-icon {
  color: #ff7e00;
  float: left;
  margin: 0 3px 5px 0;
  font-size: 20px;
}

.bot-response {
  background-color: #f0f0f0;
  border-radius: 12px;
  padding: 10px;
  text-align: left;
  font-size: 14px;
  background: linear-gradient(to bottom, #f3f3f3, #ffffff);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans', sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol', 'Noto Color Emoji';
  border:1px solid #dddddd;
  min-height: 150px;
}

.model {
  color: #444;
  font-weight: bold;
  font-size: 11px;
  vertical-align: top !important;
}

.response-metadata {
  max-width: 100%;
  border-bottom: 1px solid lightgray;
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  color: #555;
  font-size: 14px;
}


</style>
