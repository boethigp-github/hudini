<template>
  <div :class="['user-prompt', 'fade-in']">
    <div class="prompt-id">{{ $t('prompt_id', 'ID') }}: {{ promptUuid }}</div>
    <div class="prompt-tokens">
      {{ $t('prompt_tokens', 'Prompt Tokens') }}: <span style="color: #c5c5c5">{{ promptTokens }}</span>
    </div>
    <div class="prompt-text">{{ promptText }}
      <user-outlined class="user-icon"/>
    </div>
  </div>
</template>

<script>
import { UserOutlined } from '@ant-design/icons-vue';
import { List } from 'ant-design-vue';

export default {
  name: 'UserPrompt',
  components: {
    UserOutlined,
    'a-list-item': List.Item,
    'a-list-item-meta': List.Item.Meta,
  },
  props: {
    userContext: {
      type: Object,
      required: true,
    },
  },
  emits: ['mouseover', 'mouseout'],
  computed: {
    promptUuid() {
      return this.userContext?.prompt?.uuid || 'N/A';
    },
    promptTokens() {
      return this.userContext?.prompt?.context_data?.[0]?.completion?.usage?.prompt_tokens || '0';
    },
    promptText() {
      return this.userContext?.prompt?.prompt || '';
    }
  }
};
</script>

<style scoped>
.fade-in {
  animation: fadeIn 0.5s;
}

.prompt-tokens {
  font-size: 12px;
  width: 100%;
  display: block;
  margin-top: 5px;
  color: #fff;
  text-shadow: 1px 1px 0.5px rgba(0, 0, 0, 0.3);
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.prompt-text {
  width: 100%;
  word-break: break-word;
  color: #67950c;
  font-weight: bold;
  margin-top: 10px;
}

.prompt-id {
  width: 100%;
  font-size: 11px;
  color: #fff;
  text-shadow: 1px 1px 0.5px rgba(0, 0, 0, 0.3);
}

.user-prompt {
  margin-left: auto;
  margin-bottom: 10px;
  margin-top: 15px;
  width: 60%;
  max-width: 60% !important;
  background: linear-gradient(to bottom, #d9d9d9,  #f3f3f3);
  border:1px solid #dddddd;
  border-radius: 12px;
  padding: 10px;
  text-align: right;

}

.user-icon {
  color: #67950c;
  font-size: 20px;
}
</style>
