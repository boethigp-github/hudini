<template>
  <a-row>
    <a-col :span="23">
      <div id="response" class="response" ref="responseElement">
        <div>
          <div v-for="(userContext, index) in userContextList" :key="userContext.uuid">
            <!-- Render the prompt -->
            <div v-if="userContext.uuid">
              <UserPrompt
                :userContext="userContext"
                @mouseover="handleMouseOver(userContext.uuid)"
                @mouseout="handleMouseOut"
              />
            </div>

            <div style="width: 100%" v-if="userContext?.prompt?.context_data">
              <!-- Add a flexbox container -->
              <div class="bot-response-container">
                <!-- Render each BotResponse item using the flexbox layout -->
                <div
                  v-for="(contextDataItem, subIndex) in userContext.prompt.context_data"
                  :key="contextDataItem.id"
                  class="bot-response-item"
                  :style="{ width: getWidth(subIndex, userContext.prompt.context_data.length) }"
                >
                  <BotResponse
                    v-if="contextDataItem.completion"
                    :contextDataItem="contextDataItem"
                    @mouseover="handleMouseOver(contextDataItem.id)"
                    @mouseout="handleMouseOut"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <ComparisonDrawer :plugins="plugins" :responses="[]" width="90%"/>
    </a-col>

    <a-col :span="1" class="nav-container">
      <ResponsePanelMenu/>
    </a-col>
  </a-row>
</template>

<script>
import { nextTick, watch, ref, onMounted } from 'vue';
import { Row, Col } from 'ant-design-vue';
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
      if(length >=2){
         return length % 2 !== 0 ? '32.5%' : '49.5%';
      }
      return "100%";
    };

    watch(
      () => props.userContextList,
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
      scrollToBottom,
      getWidth,
    };
  },
};
</script>

<style scoped>
/* Flexbox container for BotResponse items */
.bot-response-container {
  display: flex;
  flex-wrap: wrap; /* Ensure items wrap after 3 per row */
}

.bot-response-item {
  box-sizing: border-box; /* Ensure padding and margin do not affect width */
  margin: 5px 5px 0 0
}

.nav-container {
  padding-left: 10px;
}

/* Stack items vertically for smaller screens */
@media (max-width: 768px) {
  .bot-response-item {
    width: 100% !important; /* Stack items vertically on small screens */
  }
}
</style>
