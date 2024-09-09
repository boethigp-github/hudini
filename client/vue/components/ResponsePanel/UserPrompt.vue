<template>
  <div :class="['user-prompt', 'fade-in']">
    <div class="prompt-id">{{ $t('prompt_id', 'ID') }}: {{ promptUuid }}</div>
    <div class="prompt-tokens">
      {{ $t('prompt_tokens', 'Prompt Tokens') }}: <span >{{ promptTokens }}</span>
    </div>
    <div class="prompt-text">{{ promptText }}
           <v-btn  class="panel-menu-button" icon="mdi-account" :title="$t('open_account', 'Open Account')" key="open_account"></v-btn>
    </div>
  </div>
</template>

<script>


export default {
  name: 'UserPrompt',
  components: {

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

  font-weight: bold;
  margin-top: 10px;
}

.prompt-id {
  width: 100%;
  font-size: 11px;

  text-shadow: 1px 1px 0.5px rgba(0, 0, 0, 0.3);
}

.user-prompt {
  margin-left: auto;
  margin-bottom: 10px;
  margin-top: 15px;
  width: 60%;
  max-width: 60% !important;

  border-radius: 12px;
  padding: 10px;
  text-align: right;

}

.user-icon {
  color: #1b610b;
  font-size: 20px;
}
</style>
