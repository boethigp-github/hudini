import { createRouter, createWebHistory } from 'vue-router';
import ChatForm from './components/ChatForm.vue';
import Login from './components/Auth/LoginForm.vue';
import { isAuthenticated } from '@/vue/services/api'; // Import the API-based authentication check

// Function to periodically check session status
let sessionCheckInterval = null;

const startSessionCheck = () => {
  console.log('Performing interval-based session check...');
  if (!sessionCheckInterval) {
    sessionCheckInterval = setInterval(async () => {
      console.log('Performing interval-based session check...');
      const authenticated = await isAuthenticated();
      if (!authenticated) {
        console.log('Session expired, redirecting to login');
        window.location.href = '/login';
      } else {
        console.log('Session is still valid.');
      }
    }, 30000); // Check session every 30 seconds
  }
};

const stopSessionCheck = () => {
  if (sessionCheckInterval) {
    clearInterval(sessionCheckInterval);
    sessionCheckInterval = null;
  }
};

startSessionCheck(); // Start session checks when authenticated

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
        stopSessionCheck(); // Stop session checks when logged out
        next('/login');
      } else {
        next();
      }
    },
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    beforeEnter: async (to, from, next) => {
      const authenticated = await isAuthenticated(); // Check if the user is already authenticated
      if (authenticated) {
        console.log('User already authenticated, redirecting to Home');
        next('/'); // Redirect to Home if already authenticated
      } else {
        next(); // Proceed to login if not authenticated
      }
    },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Global navigation guard
router.beforeEach(async (to, from, next) => {
  console.log(`Navigating from ${from.path} to ${to.path}`);

  // Start session check when navigating to Home or other protected routes
  if (to.path === '/' && !sessionCheckInterval) {
    startSessionCheck();
  }

  next();
});

// Stop the session check when leaving the protected routes (optional)
router.afterEach((to) => {
  if (to.path !== '/') {
    stopSessionCheck(); // Stop the session check if the user leaves the home route
  }
});

export default router;
