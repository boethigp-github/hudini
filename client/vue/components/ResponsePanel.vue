<template>
  <a-row>
    <a-col :span="23">
      <div id="response" class="response" ref="responseElement">
        <div class="flex-container">
          <template v-for="(response, index) in responses.slice().reverse()" :key="index">
            <template v-if="response.prompt">
              <div class="user-prompt-wrapper">
                <a-card dense size="small" :id="`dialog_${response.prompt_id}`" class="dialog-card user-prompt-card">
                  <UserPrompt
                    :prompt="response"
                    :isHighlighted="isHighlighted(response.prompt_id)"
                    @mouseover="handleMouseOver"
                    @mouseout="handleMouseOut"
                  />
                </a-card>
              </div>
            </template>
            <a-card v-else-if="response.completion" dense size="small" :id="`dialog_${response.prompt_id}`" class="dialog-card">
              <BotResponse
                :response="response"
                :isHighlighted="isHighlighted(response.prompt_id)"
                :hasMultipleResponses="hasMultipleResponses(response.prompt_id)"
                @mouseover="handleMouseOver"
                @mouseout="handleMouseOut"
              />
            </a-card>
          </template>
        </div>
      </div>
      <ComparisonDrawer :plugins="plugins" :responses="responses" width="90%"/>
    </a-col>

    <a-col :span="1" class="nav-container">
      <ResponsePanelMenu/>
    </a-col>
  </a-row>
</template>

<script>
import { nextTick, watch, ref, onMounted } from 'vue';
import { Row, Col, Card } from 'ant-design-vue';
import './ResponsePanel/response_panel.css';
import ResponsePanelMenu from './ResponsePanel/ResponsePanelMenu.vue';
import { markdownPlugins } from './../stores/markdownPlugins.js';
import ComparisonDrawer from './ResponsePanel/ComparisonDrawer.vue';
import UserPrompt from './ResponsePanel/UserPrompt.vue';
import BotResponse from './ResponsePanel/BotResponse.vue';

export default {
  name: 'ResponsePanel',
  components: {
    UserPrompt,
    BotResponse,
    ComparisonDrawer,
    'a-row': Row,
    'a-col': Col,
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

    const hasMultipleResponses = (prompt_id) => {
      return props.responses.filter(response => response.prompt_id === prompt_id).length > 1;
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

    watch(
      () => props.responses,
      () => {
        scrollToBottom();
      },
      { deep: true }
    );

    onMounted(() => {
      scrollToBottom();
    });

    return {
      responseElement,
      plugins: markdownPlugins,
      handleMouseOver,
      handleMouseOut,
      isHighlighted,
      scrollToBottom,
      hasMultipleResponses,
    };
  },
};
</script>

<style scoped>
.flex-container {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.dialog-card {
  flex: 1 1 30%;
  min-width: 30%;
  max-width: 100%;
}

.user-prompt-wrapper {
  width: 100%;
  margin-bottom: 10px;
}

.user-prompt-card {
  width: auto;
  max-width: 70%;
  margin-left: auto;
}

@media (max-width: 768px) {
  .dialog-card, .user-prompt-card {
    flex: 1 1 100%;
    max-width: 100%;
  }
}
</style>