<template>
  <v-switch
    v-model="model"
    :label="$t('dark_mode', 'Dark mode')"
    false-value="light"
     true-value="dark"
    @update:modelValue="toggleTheme"
  ></v-switch>
</template>

<script>

import {useI18n} from 'vue-i18n';

import {useTheme} from 'vuetify'
import {onMounted, ref} from 'vue'
export default {
  name: 'ChatForm',
  components: {
  },
  setup() {
    const theme = useTheme()
    const model = ref(null)
    const toggleTheme = () => {
      theme.global.name.value = model.value
      console.log("newTheme", model.value);
      localStorage.setItem('theme', model.value);
    }

      onMounted(() => {
      const savedTheme = localStorage.getItem('theme');
      if (savedTheme && theme) {
        model.value = savedTheme;
        theme.global.name.value = savedTheme;
      }
    });
    return {
      toggleTheme,
      model
    };
  },
};
</script>