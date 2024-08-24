import { createI18n } from 'vue-i18n';

const messages = {
    en: {
        hudini_title: 'Hudini - CPU Magician on SLM',
        select_model: 'Select Model',
        select_category: 'Select Category',
        select_category_placeholder: 'Select a category',  // Add this line
        enter_prompt: 'Enter your prompt here...',
        send_button: 'Send',
        delete: 'Delete',
        your_response: 'Your response will appear here',
        copied_to_clipboard: 'Prompt copied to clipboard',
        failed_to_copy: 'Failed to copy prompt',
        prompt_deleted: 'Prompt deleted',
        previous_prompts: 'Previous Prompts',
        no_prompts: 'No prompts saved yet',  // New key
        failed_to_prompts: 'Failed to load prompts',  // Existing key
        select_model_placeholder: 'Select one or more models',
        local_models: 'Local Models',
        openai_models: 'OpenAI Models',
        invalid_prompt: 'Invalid prompt',
        prompt_saved: 'Prompt saved successfully',
        failed_to_save_prompt: 'Failed to save prompt',
        failed_to_load_models: 'Failed to load models',
        enter_prompt_and_select_model: 'Please enter a prompt and select at least one model.',
        server_connection_error: 'An error occurred while connecting to the server.',
    },
    de: {
        hudini_title: 'Hudini - CPU Magier auf SLM',
        select_model: 'Modell auswählen',
        select_category: 'Kategorie auswählen',
        select_category_placeholder: 'Kategorie auswählen',  // Add this line
        enter_prompt: 'Geben Sie Ihren Prompt hier ein...',
        send_button: 'Senden',
        delete: 'Löschen',
        your_response: 'Ihre Antwort wird hier erscheinen',
        copied_to_clipboard: 'Prompt in die Zwischenablage kopiert',
        failed_to_copy: 'Prompt konnte nicht kopiert werden',
        prompt_deleted: 'Prompt gelöscht',
        previous_prompts: 'Bisherige Prompts',
        no_prompts: 'Noch keine Prompts gespeichert',  // New key
        failed_to_prompts: 'Fehler beim Laden der Prompts',  // Existing key
        select_model_placeholder: 'Wählen Sie ein oder mehrere Modelle aus',
        local_models: 'Lokale Modelle',
        openai_models: 'OpenAI Modelle',
        invalid_prompt: 'Ungültiger Prompt',
        prompt_saved: 'Prompt erfolgreich gespeichert',
        failed_to_save_prompt: 'Fehler beim Speichern des Prompts',
        failed_to_load_models: 'Fehler beim Laden der Modelle',
        enter_prompt_and_select_model: 'Bitte geben Sie einen Prompt ein und wählen Sie mindestens ein Modell aus.',
        server_connection_error: 'Beim Verbinden mit dem Server ist ein Fehler aufgetreten.',
    },
    fr: {
        hudini_title: 'Hudini - Magicien du CPU sur SLM',
        select_model: 'Sélectionner le modèle',
        select_category: 'Sélectionner une catégorie',
        select_category_placeholder: 'Sélectionnez une catégorie',  // Add this line
        enter_prompt: 'Entrez votre prompt ici...',
        send_button: 'Envoyer',
        delete: 'Supprimer',
        your_response: 'Votre réponse apparaîtra ici',
        copied_to_clipboard: 'Prompt copié dans le presse-papiers',
        failed_to_copy: 'Échec de la copie du prompt',
        prompt_deleted: 'Prompt supprimé',
        previous_prompts: 'Prompts Précédents',
        no_prompts: 'Aucun prompt enregistré',  // New key
        failed_to_prompts: 'Échec du chargement des prompts',  // Existing key
        select_model_placeholder: 'Sélectionnez un ou plusieurs modèles',
        local_models: 'Modèles Locaux',
        openai_models: 'Modèles OpenAI',
        invalid_prompt: 'Prompt invalide',
        prompt_saved: 'Prompt enregistré avec succès',
        failed_to_save_prompt: 'Échec de l\'enregistrement du prompt',
        failed_to_load_models: 'Échec du chargement des modèles',
        enter_prompt_and_select_model: 'Veuillez entrer un prompt et sélectionner au moins un modèle.',
        server_connection_error: 'Une erreur s\'est produite lors de la connexion au serveur.',
    },
    ru: {
        hudini_title: 'Худини - Маг ЦП на SLM',
        select_model: 'Выберите модель',
        select_category: 'Выберите категорию',
        select_category_placeholder: 'Выберите категорию',  // Add this line
        enter_prompt: 'Введите ваш запрос здесь...',
        send_button: 'Отправить',
        delete: 'Удалить',
        your_response: 'Ваш ответ появится здесь',
        copied_to_clipboard: 'Подсказка скопирована в буфер обмена',
        failed_to_copy: 'Не удалось скопировать подсказку',
        prompt_deleted: 'Подсказка удалена',
        previous_prompts: 'Предыдущие подсказки',
        no_prompts: 'Пока нет сохраненных подсказок',  // New key
        failed_to_prompts: 'Не удалось загрузить подсказки',  // Existing key
        select_model_placeholder: 'Выберите одну или несколько моделей',
        local_models: 'Локальные модели',
        openai_models: 'Модели OpenAI',
        invalid_prompt: 'Недопустимый запрос',
        prompt_saved: 'Запрос успешно сохранен',
        failed_to_save_prompt: 'Не удалось сохранить запрос',
        failed_to_load_models: 'Не удалось загрузить модели',
        enter_prompt_and_select_model: 'Пожалуйста, введите запрос и выберите хотя бы одну модель.',
        server_connection_error: 'Произошла ошибка при подключении к серверу.',
    },
    zh: {
        hudini_title: 'Hudini - SLM上的CPU魔术师',
        select_model: '选择模型',
        select_category: '选择类别',
        select_category_placeholder: '选择一个类别',  // Add this line
        enter_prompt: '在此输入您的提示...',
        send_button: '发送',
        delete: '删除',
        your_response: '您的回复将显示在此处',
        copied_to_clipboard: '提示已复制到剪贴板',
        failed_to_copy: '无法复制提示',
        prompt_deleted: '提示已删除',
        previous_prompts: '以前的提示',
        no_prompts: '尚未保存提示',  // New key
        failed_to_prompts: '加载提示失败',  // Existing key
        select_model_placeholder: '选择一个或多个模型',
        local_models: '本地模型',
        openai_models: 'OpenAI模型',
        invalid_prompt: '无效的提示',
        prompt_saved: '提示保存成功',
        failed_to_save_prompt: '保存提示失败',
        failed_to_load_models: '加载模型失败',
        enter_prompt_and_select_model: '请输入提示并至少选择一个模型。',
        server_connection_error: '连接服务器时发生错误。',
    }
};


const i18n = createI18n({
    legacy: false,
    locale: localStorage.getItem('locale') || 'de',
    fallbackLocale: 'en',
    messages,
});

export default i18n;
