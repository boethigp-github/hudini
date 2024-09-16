<template>
  <v-app-bar class="v-app-bar" name="app-bar" density="compact" :elevation="10">
    <v-container fluid>
      <v-row align="center" no-gutters>
        <v-col cols="auto">
          <img src="/assets/hudini.webp" height="40" width="40" class="mr-2" alt="Hudini logo">
        </v-col>
        <v-app-bar-title>
          Hudini greets
          <span v-if="user_info" class="username ml-2 text-primary">{{ user_info.username }}</span>
        </v-app-bar-title>
        <v-spacer></v-spacer>
        <v-col class="theme-switch-container" cols="auto">
          <ThemeSwitch />
        </v-col>
        <v-spacer></v-spacer>
        <v-col class="theme-switch-container" cols="auto">
          <FileManager />
        </v-col>
        <v-spacer></v-spacer>
        <v-col cols="auto">
          <v-btn
            class="logout"
            icon="mdi mdi-logout"
            color="primary"
            size="small"
            elevation="2"
            :title="$t('logout', 'logout')"
            @click="handleLogout"
          ></v-btn>
        </v-col>
        <v-spacer></v-spacer>
        <v-col class="language-switch-container" cols="auto">
          <LanguageSwitch />
        </v-col>
      </v-row>
    </v-container>
  </v-app-bar>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/vue/stores/currentUser';
import ThemeSwitch from "@/vue/components/ThemeSwitch.vue";
import LanguageSwitch from "@/vue/components/LanguageSwitch.vue";
import FileManager from "@/vue/components/Gripsbox/Gripsbox.vue";
import { logout } from '@/vue/services/api';

export default {
  components: {
    ThemeSwitch,
    LanguageSwitch,
    FileManager
  },
  setup() {
    const router = useRouter();
    const authStore = useAuthStore();
    const user_info = ref('');

    onMounted(async () => {
      const userData = await authStore.loadFromStorage();
      user_info.value = userData?.accessToken?.user_info;
    });

    const handleLogout = async () => {
      try {
        await logout();
        await authStore.removeUser();
        user_info.value = '';  // Clear the user info
        await router.push('/login');
      } catch (error) {
        console.error('Error during logout:', error);
      }
    };

    return {
      user_info,
      handleLogout
    };
  }
};
</script>

<style scoped>


.logout {
  margin-top: -10px;
}

.username {
  font-size: 0.9em;
  font-weight: normal;
  opacity: 0.8;
}

.v-app-bar {
  max-height: 48px;
  padding-top: 3px;
}
.theme-switch-container,
.language-switch-container {
  display: flex;
  align-items: center;
}

.theme-switch-container {
  margin-top: 15px;
}
</style>