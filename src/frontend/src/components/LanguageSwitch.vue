<template>
    <a-select v-model:value="selectedLanguage" @change="changeLanguage" class="language_switch" id="language-switch">
        <a-select-option value="en">English</a-select-option>
        <a-select-option value="de">Deutsch</a-select-option>
        <a-select-option value="fr">Français</a-select-option>
        <a-select-option value="ru">Русский</a-select-option>
        <a-select-option value="zh">中文</a-select-option>
    </a-select>
</template>

<script>
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';

export default {
    name: 'LanguageSwitch',
    setup() {
        const { locale } = useI18n();
        const selectedLanguage = ref(locale.value || 'de');

        const changeLanguage = (value) => {
            locale.value = value;
            localStorage.setItem('locale', value);
        };

        return {
            selectedLanguage,
            changeLanguage,
        };
    },
};
</script>

<style scoped>
.language_switch {
    width: 120px;
    float: right;
}
</style>
