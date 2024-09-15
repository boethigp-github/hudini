import { createRouter, createWebHistory } from 'vue-router';
import ChatForm from './components/ChatForm.vue';
import Login from './components/Auth/LoginForm.vue';
import { fetchAccessToken } from '@/vue/services/api';
import { useAuthStore } from '@/vue/stores/currentUser.js';

let sessionCheckInterval = null;

async function checkAndUpdateAccessToken() {
  const authStore = useAuthStore();
  const accessToken = await fetchAccessToken();
  authStore.setUser({ accessToken });
  return accessToken;
}

function handleAuthRedirect(accessToken, currentPath, next) {
  if (!accessToken && currentPath !== '/login') {
    console.log('User not authenticated, redirecting to login');
    next('/login');
  } else if (accessToken && currentPath === '/login') {
    console.log('User already authenticated, redirecting to Home');
    next('/');
  } else {
    next();
  }
}

const startSessionCheck = () => {
  if (!sessionCheckInterval) {
    sessionCheckInterval = setInterval(async () => {
      console.log('Performing interval-based session check...');
      const accessToken = await checkAndUpdateAccessToken();
      if (!accessToken) {
        console.log('Session expired, redirecting to login');
        const authStore = useAuthStore();
        await authStore.removeUser();
        window.location.href = '/login';
      } else {
        console.log('Session is still valid.');
      }
    }, 30000);
  }
};

const stopSessionCheck = () => {
  if (sessionCheckInterval) {
    clearInterval(sessionCheckInterval);
    sessionCheckInterval = null;
  }
};

const routes = [
  {
    path: '/',
    name: 'Home',
    component: ChatForm,
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to, from, next) => {
  console.log(`Navigating from ${from.path} to ${to.path}`);

  const accessToken = await checkAndUpdateAccessToken();
  handleAuthRedirect(accessToken, to.path, next);

  if (to.path === '/' && accessToken && !sessionCheckInterval) {
    startSessionCheck();
  }
});

router.afterEach((to) => {
  if (to.path !== '/') {
    stopSessionCheck();
  }
});

export default router;