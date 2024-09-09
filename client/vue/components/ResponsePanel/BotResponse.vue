<template>
  <div :class="['response-item','bot-response', 'fade-in']"
       @mouseover="$emit('mouseover', contextDataItem.id)"
       @mouseout="$emit('mouseout', contextDataItem.id)">
    <div class="response-metadata">
      <span class="model"> <v-btn size="x-small" class="panel-menu-button" icon="mdi-robot-happy" :title="$t('open_account', 'Open Account')" key="open_account"></v-btn>{{ getModel() }} </span>
      <span class="timestamp">{{getCompletionId()}} </span>
      <span class="timestamp">{{getUuid()}} </span>
      <span class="timestamp">{{ getPromptTokens() }}</span>
      <span class="timestamp">{{ getCompletionTokens() }}</span>
      <span class="timestamp">{{ getTotalTokens() }}</span>
      <span class="timestamp">{{ getRunTime() }}</span>
    </div>
    <Markdown
        class="bot-answer-md"
        :breaks="true"
        :plugins="getPlugins()"
        :source="contextDataItem?.completion?.choices[0].message.content"
    />

  </div>
</template>

<script>
import Markdown from 'vue3-markdown-it';
import {markdownPlugins} from './../../stores/markdownPlugins.js';

export default {
  name: 'BotResponse',
  components: {
    Markdown
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

    ];


    const getModel = () => {
      return `Model: ${props.contextDataItem.completion?.model}`;
    };

    const getUuid = () => {
      return `UUID: ${props.contextDataItem.id}`;
    };

    const getCompletionId = () => {
      return `Completion ID: ${props.contextDataItem.completion.id}`;
    };


    const getPromptTokens = () => {
      return `Prompt Tokens: ${props.contextDataItem.completion?.usage?.prompt_tokens}`;
    };


    const getCompletionTokens = () => {
      return `Completion Tokens: ${props.contextDataItem.completion?.usage?.completion_tokens}`;
    };


    const getTotalTokens = () => {
      return `Total Tokens: ${props.contextDataItem.completion?.usage?.total_tokens}`;
    };


    const getRunTime = () => {
      const start = props.contextDataItem.completion?.usage?.started;
      const end = props.contextDataItem.completion?.usage?.ended;
      const duration = end - start;
      const seconds = ((duration % 60000) / 1000).toFixed(2);
      return `Run Time: ${seconds} s`;
    };


    const getPlugins = () => markdownPlugins;

    return {
      actions,
      getModel,
      getPromptTokens,
      getCompletionTokens,
      getTotalTokens,
      getRunTime,
      getPlugins,
      getCompletionId,
      getUuid
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
  padding: 10px;
  text-align: left;
  font-size: 14px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans', sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol', 'Noto Color Emoji';
  min-height: 150px;
}

.model {
  color: #da6e00;
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
