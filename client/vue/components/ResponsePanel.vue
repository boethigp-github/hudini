<template>
  <div id="response" class="response" ref="responseElement">
    <v-virtual-scroll
        v-if="userContextList.length"
        :items="userContextList">
      <template v-slot:default="{ item }">
        <v-card dense>
          <UserPrompt
              v-if="item.uuid"
              :userContext="item"
              @mouseover="handleMouseOver(item.uuid)"
              @mouseout="handleMouseOut"
          />
          <v-card
              v-if="item?.prompt?.context_data"
              v-for="(contextDataItem, subIndex) in item.prompt.context_data"
              :key="contextDataItem.id"
          >
            <BotResponse
                v-if="contextDataItem.completion"
                :contextDataItem="contextDataItem"
                @mouseover="handleMouseOver(contextDataItem.id)"
                @mouseout="handleMouseOut"
            />
          </v-card>
        </v-card>
      </template>
    </v-virtual-scroll>
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

    const handleMouseOver = (prompt_id) => {
    };

    const handleMouseOut = () => {
    };

    const scrollToBottom = () => {
      nextTick(() => {
        if (responseElement.value) {
          responseElement.value.scrollTop = responseElement.value.scrollHeight;
        }
      });
    };

    const getWidth = (index, length) => {
      // if(length >=2){
      //    return length % 2 !== 0 ? '32.5%' : '49.5%';
      // }
      return "100%";
    };

    watch(
        () => props.userContextList,
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
      plugins: markdownPlugins,
      handleMouseOver,
      handleMouseOut,
      scrollToBottom,
      getWidth,
    };
  },
};
</script>

<style scoped>
/* Flexbox container for BotResponse items */


/* Stack items vertically for smaller screens */
@media (max-width: 768px) {
  .bot-response-item {
    width: 100% !important; /* Stack items vertically on small screens */
  }
}
</style>
