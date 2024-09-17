<template>
  <div :class="['response-item','bot-response', 'fade-in']"
       @mouseover="$emit('mouseover', contextDataItem.id)"
       @mouseout="$emit('mouseout', contextDataItem.id)">
    <div class="response-metadata">
      <span class="model">
        <v-btn size="x-small" class="panel-menu-button" icon="mdi-robot-happy"
               :title="$t('open_account', 'Open Account')" key="open_account"></v-btn>
        {{ getModel() }}
      </span>
      <span class="timestamp">{{ getCompletionId() }} </span>
      <span class="timestamp">{{ getUuid() }} </span>
      <span class="timestamp">{{ getPromptTokens() }}</span>
      <span class="timestamp">{{ getCompletionTokens() }}</span>
      <span class="timestamp">{{ getTotalTokens() }}</span>
      <span class="timestamp">{{ getRunTime() }}</span>
    </div>

    <Markdown
        v-if="typeof processedContent === 'string'"
        class="bot-answer-md"
        :breaks="true"
        :html="true"
        :plugins="getPlugins()"
        :source="processedContent"
    />

  </div>
</template>

<script>
import {ref, watchEffect} from 'vue';
import Markdown from 'vue3-markdown-it';
import {markdownPlugins} from './../../stores/markdownPlugins.js';
import {callTool, parseCallContent} from "@/vue/services/api.js";

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
    const processedContent = ref('');

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


    const objectToMarkdownString = (obj, indent = '') => {
      if (typeof obj !== 'object' || obj === null) {
        return `\`${String(obj)}\``;
      }

      let markdown = '';
      for (const [key, value] of Object.entries(obj)) {
        markdown += `${indent} ${key}: `;
        if (typeof value === 'object' && value !== null) {
          markdown += '\n' + objectToMarkdownString(value, indent + '  ');
        } else {
          markdown += `\`${String(value)}\``;
        }
        markdown += '\n';
      }
      return markdown.trim();
    };

const processToolCalling = async (content) => {
  let processedContent = parseCallContent(content);

  console.log("111111111111", processedContent);

  if (!processedContent || !processedContent.tool) {
    return content;
  }

  try {
    let response = await callTool(processedContent);
    if (!response) {
      return content;
    }

    console.log("response", response);

    // Convert the response object to a Markdown string
    const markdownString = objectToMarkdownString(response);

      // Replace the original JSON in the content with the Markdown string, removing the ```json prefix
    const updatedContent = "<div>"+content.replace(/```json\s*\{[\s\S]*\}\s*/, markdownString).replace(/```/g, "")+"</div>"

    return updatedContent;
  } catch (error) {
    console.error("Error processing tool call:", error);
  }

  return content;
};


    watchEffect(async () => {
      const content = props.contextDataItem?.completion?.choices[0]?.message?.content;
      if (content) {
        processedContent.value = await processToolCalling(content);
      }
    });

    return {
      getModel,
      getPromptTokens,
      getCompletionTokens,
      getTotalTokens,
      getRunTime,
      getPlugins,
      getCompletionId,
      getUuid,
      processedContent,
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

.tool-running {
  font-style: italic;
  color: #ff9800;
}
</style>