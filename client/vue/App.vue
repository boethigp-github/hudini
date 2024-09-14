<template>
  <div id="app">
    <v-app>
      <template v-if="isLoggedIn">
        <ChatForm />
      </template>
      <template v-else>
        <Login @login-success="handleLoginSuccess" />
      </template>
    </v-app>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import ChatForm from './components/ChatForm.vue';
import Login from './components/Auth/LoginForm.vue';

export default {
  components: {
    ChatForm,
    Login,
  },
  setup() {
    const isLoggedIn = ref(false);

    const checkLoginStatus = () => {
      const token = localStorage.getItem('userToken');
      isLoggedIn.value = !!token;
    };

    const handleLoginSuccess = () => {
      isLoggedIn.value = true;
    };

    onMounted(() => {
      checkLoginStatus();
    });

    return {
      isLoggedIn,
      handleLoginSuccess,
    };
  },
};
</script>

<style>
/* Add any global styles here */
</style>