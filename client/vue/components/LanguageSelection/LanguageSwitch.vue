<template>
  <v-select
    v-model="selectedLanguage"
    @update:modelValue="changeLanguage"
    class="language_switch"
    id="language-switch"
    :items="languages"
    item-text="title"
    item-value="id"
  ></v-select>
</template>

<script>
import {ref} from 'vue';
import {useI18n} from 'vue-i18n';

export default {
  name: 'LanguageSwitch',
  setup() {
    const {locale} = useI18n();
    const selectedLanguage = ref(locale.value || 'de');

    const languages = [
      {title: 'Deutsch', id: 'de'},
      {title: 'English', id: 'en'},
      {title: 'Russian', id: 'ru'},
      {title: 'Chinese', id: 'zh'}
    ];

    const changeLanguage = (value) => {
      locale.value = value;
      localStorage.setItem('locale', value);
    };

    return {
      selectedLanguage,
      changeLanguage,
      languages,  // Return das Array für v-select
    };
  },
};
</script>

<style scoped>
.language_switch {
  max-width: 320px;
  margin-right: 3px;
}
</style>
