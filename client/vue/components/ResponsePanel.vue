<template>
  <div id="response" class="response" ref="responseElement">
    <div v-if="userContextList.length" class="response-content">
      <v-card
          v-for="item in userContextList"
          :key="item.uuid"
          dense
          class="response-item"
      >
        <UserPrompt
            :userContext="item"
            @mouseover="handleMouseOver(item.uuid)"
            @mouseout="handleMouseOut"
        />
        <v-card
            v-if="item?.prompt?.context_data"
            v-for="contextDataItem in item.prompt.context_data"
            class="user-prompt-item"
            :key="contextDataItem.id"
        >
          <BotResponse
              class="bot-response-item"
              v-if="contextDataItem.completion"
              :contextDataItem="contextDataItem"
              @mouseover="handleMouseOver(contextDataItem.id)"
              @mouseout="handleMouseOut"
          />
        </v-card>
      </v-card>
    </div>
  </div>
</template>

<script>
import {nextTick, watch, ref, onMounted} from 'vue';
import './ResponsePanel/response_panel.css';
import ResponsePanelMenu from './ResponsePanel/ResponsePanelMenu.vue';
import {markdownPlugins} from './../stores/markdownPlugins.js';
import 'highlight.js/styles/googlecode.css';
import './ResponsePanel/Highlite.css';
import UserPrompt from './ResponsePanel/UserPrompt.vue';
import BotResponse from './ResponsePanel/BotResponse.vue';

export default {
  name: 'ResponsePanel',
  components: {
    UserPrompt,
    BotResponse,
    ResponsePanelMenu,
  },
  props: {
    userContextList: {
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

    const handleMouseOver = (id) => {

    };

    const handleMouseOut = () => {

    };

    const scrollToBottom = () => {
      nextTick(() => {
        setTimeout(() => {
          if (responseElement.value) {
            responseElement.value.scrollTop = responseElement.value.scrollHeight;
          }
        }, 100); // Small delay to ensure content is rendered
      });
    };

    watch(() => props.userContextList.length, (newLength, oldLength) => {
      scrollToBottom();
    });

    watch(() => props.userContextList, () => {
      scrollToBottom();
    }, {deep: true});

    onMounted(() => {
      scrollToBottom();
    });

    return {
      responseElement,
      plugins: markdownPlugins,
      handleMouseOver,
      handleMouseOut,
      scrollToBottom,
    };
  },
};
</script>

<style scoped>
.response {
  height: 80vh;
  overflow-y: auto;
  scroll-behavior: smooth;
}



.response-content {
  display: flex;
  flex-direction: column;
}

.response-item {
  margin-bottom: 16px;
}

@media (max-width: 768px) {
  .bot-response-item {
    width: 100% !important;
  }
}
</style>