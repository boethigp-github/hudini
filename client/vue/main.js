import { createApp } from 'vue';
import App from './App.vue';
import Antd from 'ant-design-vue';
import 'ant-design-vue/dist/reset.css'; // Correct import for Ant Design Vue styles
import './assets/chat-styles.css';
import i18n from './i18n.js';
import { createPinia } from 'pinia'
const app = createApp(App);


app.use(createPinia())
app.use(Antd);
app.use(i18n);
app.mount('#app');
