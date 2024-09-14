import { createRouter, createWebHistory } from 'vue-router';
import ChatForm from './components/ChatForm.vue';
import Login from './components/Auth/LoginForm.vue';

// Function to check login status based on the cookie
const isAuthenticated = () => {
  console.log('isAuthenticated function called');
  const cookies = document.cookie.split('; ');
  console.log('isAuthenticated cookies', cookies);
  const sessionCookie = cookies.find(cookie => cookie.startsWith('session'));
  return !!sessionCookie;
};

const routes = [
  {
    path: '/',
    name: 'Home',
    component: ChatForm,
    beforeEnter: (to, from, next) => {
      console.log('Entering beforeEnter guard for Home route');
      if (!isAuthenticated()) {
        console.log('User not authenticated, redirecting to login');
        next('/login');
      } else {
        console.log("User authenticated, cookies:", document.cookie.split('; '));
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

// Global navigation guard
router.beforeEach((to, from, next) => {
  console.log(`Navigating from ${from.path} to ${to.path}`);
  next();
});

export default router;