import { createI18n } from 'vue-i18n';

// Deine Sprachdateien
const messages = {
    en: {
        hudini_title: 'Hudini - CPU Magician on SLM',
        select_model: 'Select Model',
        enter_prompt: 'Enter your prompt here...',
        send_button: 'Send',
        delete: 'Delete',
        your_response: 'Your response will appear here',
        copied_to_clipboard: 'Prompt copied to clipboard',
        failed_to_copy: 'Failed to copy prompt',
        prompt_deleted: 'Prompt deleted',
        previous_prompts: 'Previous Prompts',
    },
    de: {
        hudini_title: 'Hudini - CPU Magier auf SLM',
        select_model: 'Modell auswählen',
        enter_prompt: 'Geben Sie Ihren Prompt hier ein...',
        send_button: 'Senden',
        delete: 'Löschen',
        your_response: 'Ihre Antwort wird hier erscheinen',
        copied_to_clipboard: 'Prompt in die Zwischenablage kopiert',
        failed_to_copy: 'Prompt konnte nicht kopiert werden',
        prompt_deleted: 'Prompt gelöscht',
        previous_prompts: 'Bisherige Prompts',
    },
    fr: {
        hudini_title: 'Hudini - Magicien du CPU sur SLM',
        select_model: 'Sélectionner le modèle',
        enter_prompt: 'Entrez votre prompt ici...',
        send_button: 'Envoyer',
        delete: 'Supprimer',
        your_response: 'Votre réponse apparaîtra ici',
        copied_to_clipboard: 'Prompt copié dans le presse-papiers',
        failed_to_copy: 'Échec de la copie du prompt',
        prompt_deleted: 'Prompt supprimé',
        previous_prompts: 'Prompts Précédents',
    },
    ru: {
        hudini_title: 'Худини - Маг ЦП на SLM',
        select_model: 'Выберите модель',
        enter_prompt: 'Введите ваш запрос здесь...',
        send_button: 'Отправить',
        delete: 'Удалить',
        your_response: 'Ваш ответ появится здесь',
        copied_to_clipboard: 'Подсказка скопирована в буфер обмена',
        failed_to_copy: 'Не удалось скопировать подсказку',
        prompt_deleted: 'Подсказка удалена',
        previous_prompts: 'Предыдущие подсказки',
    },
    zh: {
        hudini_title: 'Hudini - SLM上的CPU魔术师',
        select_model: '选择模型',
        enter_prompt: '在此输入您的提示...',
        send_button: '发送',
        delete: '删除',
        your_response: '您的回复将显示在此处',
        copied_to_clipboard: '提示已复制到剪贴板',
        failed_to_copy: '无法复制提示',
        prompt_deleted: '提示已删除',
        previous_prompts: '以前的提示',
    }
};

// Erstelle die i18n Instanz
const i18n = createI18n({
    legacy: false, // Deaktiviere den Legacy-Modus für Vue 3
    locale: localStorage.getItem('locale') || 'de',
    fallbackLocale: 'en',
    messages,
});

export default i18n;
