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
                <!-- Add the spinner here, it will be shown only when loading is true -->

        </v-card>
      </v-card>
<!--          <v-progress-linear-->
<!--      v-if="loading"-->
<!--      indeterminate-->
<!--      color="secondary"-->
<!--      height="20"-->
<!--      class="thinking-spinner"-->
<!--    >-->
<!--      Thinking...-->
<!--    </v-progress-linear>-->
    </div>
  </div>
</template>

<script>
import {nextTick, watch, ref, onMounted} from 'vue';
import './response_panel.css';
import ResponsePanelMenu from './ResponsePanelMenu.vue';
import {markdownPlugins} from '../../stores/markdownPlugins.js';
import 'highlight.js/styles/googlecode.css';
import './Highlite.css';
import UserPrompt from './UserPrompt.vue';
import BotResponse from './BotResponse.vue';

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
    height: 82.5vh!important;
    max-height:82.5vh;
    overflow-y: auto; /* Ermöglicht vertikales Scrollen */
    font-family: 'Georgia', Tahoma, Geneva, Verdana, sans-serif;
    display: flex;
    scroll-behavior: smooth;
    flex-direction: column-reverse; /* Damit neuer Text unten erscheint */
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