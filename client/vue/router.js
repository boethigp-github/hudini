import { createRouter, createWebHistory } from 'vue-router';
import ChatForm from './components/ChatForm.vue';
import Login from './components/Auth/LoginForm.vue';
import { isAuthenticated } from '@/vue/services/api'; // Import the API-based authentication check

const routes = [
  {
    path: '/',
    name: 'Home',
    component: ChatForm,
    beforeEnter: async (to, from, next) => {
      console.log('Checking if user is authenticated from server...');
      const authenticated = await isAuthenticated(); // Call the server to check authentication
      if (!authenticated) {
        console.log('User not authenticated, redirecting to login');
        next('/login');
      } else {
        console.log('User is authenticated, allowing access to Home');
        next();
      }
    },
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

export default router;
