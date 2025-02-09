<template>
  <v-container class="login-container">
    <v-card class="mx-auto pa-4" max-width="400">
      <v-card-title class="text-h5 mb-4">
        {{ isLogin ? 'Login' : 'Register' }}
      </v-card-title>
      <v-form @submit.prevent="handleSubmit">
        <v-text-field
          v-model="email"
          label="Email"
          type="email"
          autocomplete="username"
          required
          :rules="[v => !!v || 'Email is required', v => /.+@.+\..+/.test(v) || 'E-mail must be valid']"
        ></v-text-field>
        <v-text-field
          v-model="password"
          label="Password"
          type="password"
          :autocomplete="isLogin ? 'current-password' : 'new-password'"
          required
          :rules="[v => !!v || 'Password is required', v => v.length >= 6 || 'Password must be at least 6 characters']"
        ></v-text-field>
        <v-btn
          type="submit"
          color="primary"
          block
          class="mt-4"
          :loading="loading"
          :disabled="loading || googleLoading"
        >
          {{ isLogin ? 'Login' : 'Register' }}
        </v-btn>
      </v-form>
      <v-divider class="my-4"></v-divider>
      <v-btn
        color="red"
        block
        @click="handleGoogleAuth"
        :loading="googleLoading"
        :disabled="loading || googleLoading"
      >
        <v-icon left>mdi-google</v-icon>
        Sign in with Google
      </v-btn>
      <v-card-text class="text-center mt-4">
        {{ isLogin ? "Don't have an account?" : "Already have an account?" }}
        <v-btn
          variant="text"
          color="primary"
          @click="toggleMode"
          class="ml-2"
        >
          {{ isLogin ? 'Register' : 'Login' }}
        </v-btn>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { loginWithEmailPassword, initiateGoogleAuth } from '@/vue/services/api';

const emit = defineEmits(['login-success']);

const email = ref('');
const password = ref('');
const isLogin = ref(true);
const loading = ref(false);
const googleLoading = ref(false);

const toggleMode = () => {
  isLogin.value = !isLogin.value;
  email.value = '';
  password.value = '';
};

const handleSubmit = async () => {
  loading.value = true;
  try {
    const data = await loginWithEmailPassword(email.value, password.value);
    localStorage.setItem('userToken', data.token);
    emit('login-success');
  } catch (error) {

  } finally {
    loading.value = false;
  }
};

const handleGoogleAuth = async () => {
  googleLoading.value = true;
  try {
    const data = await initiateGoogleAuth();
    window.location.href = data.redirect_url;
  }finally {

  }
};

onMounted(() => {
  // Any mounting logic if needed
});
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>