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
        :plugins="getPlugins()"
        :source="processedContent"
    />

  </div>
</template>

<script>
import {ref, watchEffect} from 'vue';
import Markdown from 'vue3-markdown-it';
import {markdownPlugins} from './../../stores/markdownPlugins.js';
import {callTool} from "@/vue/services/api.js";

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

    const processHudiniWants = async (content) => {


      let processedContent = parseCallContent(content)

      if (!processedContent || !processedContent.name) {
        return content;
      }

      try {
        let response = await callTool(processedContent);

        if (!response) {
          return content;
        }

        return response
      } catch (error) {
        console.error("Error processing HUDINI_WANTS:", error);

      }

      return processedContent;
    };


    function parseCallContent(input) {
      // Updated regex to match JSON content within ```json ``` backticks
      const regex = /```json\s*([\s\S]*?)\s*```/;

      // Extract the content
      const match = input.match(regex);

      if (match && match[1]) {
        try {
          // Parse the extracted content as JSON
          return JSON.parse(match[1]);
        } catch (error) {
          console.error("Error parsing JSON:", error);
          return null;
        }
      } else {
        console.log("No JSON content found");
        return input;
      }
    }

    watchEffect(async () => {
      const content = props.contextDataItem?.completion?.choices[0]?.message?.content;
      if (content) {
        processedContent.value = await processHudiniWants(content);
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
/* Styles remain unchanged */
</style>