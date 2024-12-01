import { createApp } from 'vue';
import App from './App.vue';
import 'vuetify/styles';
import { createVuetify } from 'vuetify';
import * as components from 'vuetify/components';
import * as directives from 'vuetify/directives';
import './assets/chat-styles.css';
import '@mdi/font/css/materialdesignicons.css';
import { aliases, mdi } from 'vuetify/iconsets/mdi';
import colors from 'vuetify/lib/util/colors';


import router from './router';

const myAllBlackTheme = {
  dark: true,
  colors: {
    background: "#000000",
    surface: "#0d171b",
    primary: "#990000",
    "primary-darken-1": "#770000",
    secondary: "#990000",
    "secondary-darken-1": "#770000",
    error: "#FF5252",
    info: "#2196F3",
    success: "#4CAF50",
    warning: "#FFC107",
  },
};

const vuetify = createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: "myAllBlackTheme",
    themes: {
      myAllBlackTheme,
    },
  },
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: {
      mdi,
    },
  },
});

import i18n from './i18n.js';
import { createPinia } from 'pinia';

const app = createApp(App);

app.use(createPinia());
app.use(vuetify);
app.use(i18n);

// Füge den Router hinzu
app.use(router);  // Verwende den Router in der App

app.mount('#app');
