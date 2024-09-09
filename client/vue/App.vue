<template>
  <div id="app">
      <v-app>
        <ChatForm/>
      </v-app>
  </div>
</template>

<script>
import ChatForm from './components/ChatForm.vue';

export default {
  components: {
    ChatForm,
  },
};
</script>

<style>
/* Add any global styles here */
</style>
