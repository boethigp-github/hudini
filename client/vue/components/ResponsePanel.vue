<template>
  <div id="response" class="response">

    <div v-for="(item, index) in responses"
         :key="index"
         :class="[item.status === 'complete' ? 'response-item' : 'incomplete-item']"
    >
      <div v-if="item.prompt" class="user-prompt">
        {{item.prompt}}
      </div>

      <div v-if="item.completion?.choices?.length">
        <div class="response-metadata" >
          <span class="model">{{ $t('model') }}: {{ item.model }}</span><br>
          <span class="timestamp">{{ formatTimestamp(item.completion.created) }}</span>
        </div>
        <div class="response-content" >
          {{ item.completion.choices[0].message.content}}
        </div>
      </div>
      <div v-else>
        <div class="response-metadata" v-if="item.model">
          <span class="model">{{ $t('model') }}: {{ item.model }}</span>
        </div>
        <div class="response-content" >
          {{ item.error}}
        </div>
      </div>
    </div>

    <!-- Placeholder message if no responses are present -->
    <div v-if="responses.length === 0" class="placeholder">
      {{ $t('your_response') }}
    </div>
  </div>
</template>

<script>
import { nextTick, watch } from 'vue';

export default {
  name: 'ResponsePanel',
  props: {
    responses: {
      type: Array,
      required: true,
      default: () => [],
    },
  },
  setup(props) {
    const scrollToBottom = () => {
      nextTick(() => {
        const responseElement = document.getElementById('response');
        responseElement.scrollTop = responseElement.scrollHeight;
      });
    };

    const formatTimestamp = (timestamp) => {
      const date = new Date(timestamp * 1000); // Multiply by 1000 if the timestamp is in seconds

      // Format the date to YYYY-MM-DD HH:ii:ss
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0'); // Months are 0-indexed
      const day = String(date.getDate()).padStart(2, '0');
      const hours = String(date.getHours()).padStart(2, '0');
      const minutes = String(date.getMinutes()).padStart(2, '0');
      const seconds = String(date.getSeconds()).padStart(2, '0');

      return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
    };

    watch(
        () => props.responses,
        () => {
          scrollToBottom();
        },
        { deep: true } // Ensure deep watching of the array's content
    );

    return {
      scrollToBottom,
      formatTimestamp,
    };
  }
};
</script>

<style scoped>
.response {
  max-height: 48vh;
  height: 48vh;
  overflow-y: auto;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  background-color: #f9f9f9;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
}

.response-item, .user-prompt{
  border: none;
  border-radius: 10px;
  padding: 10px;
  background: #eeeeee;
  margin-top: 10px;
  float: left;
  max-width:100%;
}

.user-prompt{
  border: none;
  background: lightgrey;
  float: right;
  max-width: 80%;
}
.incomplete-item {
  border: none;
  margin-top: 10px;
  border: #4CAF50;
}

.response-metadata {
  justify-content: space-between;
  margin-bottom: 5px;
  color: #666;
  font-size: 0.875rem;
}

.timestamp {
  font-size: 12px;
  color: #666;
}

.model {
  color: #999;
  font-weight: bold;
  margin-top: -5px;
}

.response-content {
  font-size: 0.9rem;
  color: #333;
}

.placeholder {
  color: #aaa;
}
</style>
