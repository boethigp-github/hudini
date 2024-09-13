import {createI18n} from 'vue-i18n';

const messages = {
    en: {
        hudini_title: 'Hudini - CPU Magician on SLM',
        select_model: 'Select Model',
        model: 'Model',
        select_category: 'Select Category',
        select_category_placeholder: 'Select a category',
        enter_prompt: 'Enter your prompt here...',
        send_button: 'Send',
        delete: 'Delete',
        your_response: 'Your response will appear here',
        copied_to_clipboard: 'Prompt copied to clipboard',
        failed_to_copy: 'Failed to copy prompt',
        prompt_deleted: 'Prompt deleted',
        previous_prompts: 'Previous Prompts',
        no_prompts: 'No prompts saved yet',
        failed_to_prompts: 'Failed to load prompts',
        select_model_placeholder: 'Select one or more models',
        local_models: 'Local Models',
        openai_models: 'OpenAI Models',
        invalid_prompt: 'Invalid prompt',
        prompt_saved: 'Prompt saved successfully',
        failed_to_save_prompt: 'Failed to save prompt',
        failed_to_load_models: 'Failed to load models',
        enter_prompt_and_select_model: 'Please enter a prompt and select at least one model.',
        server_connection_error: 'An error occurred while connecting to the server.',
        select_category_and_model: 'Please select a category and model',
        model_responses: 'Model Responses',
        prompts: 'Prompts',
        models: 'Models',
        compare: 'Compare',
        model_selection: 'Model Selection',
        prompt_submission: 'Prompt Submission',
        content: 'Content',
        timestamp: 'Timestamp',
        error: 'Error',
        model_comparison: 'Model Comparison',
        user_prompt: 'User Prompt',
        no_error: 'No error',
        copy_clipboard: 'Copy to clipboard',
        comparison_view: 'Comparison View',
        delete_thread: 'Delete Thread',
        delete_thread_confirmation_title: 'Are you sure you want to delete this thread?',
        delete_thread_confirmation_content: 'This action cannot be undone.',
        delete_thread_ok_text: 'Yes, delete it',
        delete_thread_cancel_text: 'No, keep it',
        delete_thread_cancel_log: 'Deletion canceled',
        rerun_prompt: 'Rerun Prompt',
        failed_to_retrieve_user_context: 'Failed to retrieve user context',
        no_data_to_compare: 'No data to compare',
        statistics: 'Statistics',
        system_prompts: 'System Prompts',
        completion_tokens: 'Completion Tokens',
        prompt_tokens: 'Prompt Tokens',
        all_tokens: 'All Tokens',
        run_time: 'Run Time',
        total_tokens: "Total Tokens",
        prompt_id: 'Prompt ID',
        dark_mode: 'Dark Mode',
        search_prompts: 'Search prompts',
        open_account: 'Open Account',
        completion_content: 'Completion Content',
        close_comparison: 'Close Comparison',
        confirm_delete: 'Confirm Delete',
        delete_thread_confirmation: 'Are you sure you want to delete this thread?',
        cancel: 'Cancel',
        failed_to_delete_thread: 'Failed to delete thread',
        export_to_excel: "Export to Excel",
        publish_social_media: "Publish in Social Media",
        select_social_media: "Select Social Media Accounts",
        publish: "Publish",
        provider: 'Provider',
        generate_image: 'Generate Image',
        image_prompt: 'Enter an image description...',
        group: 'Group',
        open_context_manager: "Open Context Manager",
        hudinis_gripsbox: "Hudini's Gripsbox",
        upload_files: "Upload Files",
        assign_tags: "Assign Tags",
        active: "Active",
        close: "Close"

    },
    de: {
        hudini_title: 'Hudini - CPU Magier auf SLM',
        select_model: 'Modell auswählen',
        model: 'Modell',
        select_category: 'Kategorie auswählen',
        select_category_placeholder: 'Kategorie auswählen',
        enter_prompt: 'Geben Sie Ihren Prompt hier ein...',
        send_button: 'Senden',
        delete: 'Löschen',
        your_response: 'Ihre Antwort wird hier erscheinen',
        copied_to_clipboard: 'Prompt in die Zwischenablage kopiert',
        failed_to_copy: 'Prompt konnte nicht kopiert werden',
        prompt_deleted: 'Prompt gelöscht',
        previous_prompts: 'Bisherige Prompts',
        no_prompts: 'Noch keine Prompts gespeichert',
        failed_to_prompts: 'Fehler beim Laden der Prompts',
        select_model_placeholder: 'Wählen Sie ein oder mehrere Modelle aus',
        local_models: 'Lokale Modelle',
        openai_models: 'OpenAI Modelle',
        invalid_prompt: 'Ungültiger Prompt',
        prompt_saved: 'Prompt erfolgreich gespeichert',
        failed_to_save_prompt: 'Fehler beim Speichern des Prompts',
        failed_to_load_models: 'Fehler beim Laden der Modelle',
        enter_prompt_and_select_model: 'Bitte geben Sie einen Prompt ein und wählen Sie mindestens ein Modell aus.',
        server_connection_error: 'Beim Verbinden mit dem Server ist ein Fehler aufgetreten.',
        select_category_and_model: 'Bitte wählen Sie eine Kategorie und ein Modell',
        model_responses: 'Modellantworten',
        prompts: 'Prompts',
        models: 'Modelle',
        compare: 'Vergleichen',
        model_selection: 'Modellauswahl',
        prompt_submission: 'Eingabeaufforderung',
        content: 'Inhalt',
        timestamp: 'Zeitstempel',
        error: 'Fehler',
        model_comparison: 'Modellvergleich',
        user_prompt: 'Userprompt',
        no_error: 'Kein Fehler',
        copy_clipboard: 'In die Zwischenablage kopieren',
        comparison_view: 'Vergleichsansicht',
        delete_thread: 'Thread löschen',
        delete_thread_confirmation_title: 'Sind Sie sicher, dass Sie diesen Thread löschen möchten?',
        delete_thread_confirmation_content: 'Diese Aktion kann nicht rückgängig gemacht werden.',
        delete_thread_ok_text: 'Ja, löschen',
        delete_thread_cancel_text: 'Nein, behalten',
        delete_thread_cancel_log: 'Löschung abgebrochen',
        rerun_prompt: 'Prompt erneut ausführen',
        failed_to_retrieve_user_context: 'Fehler beim Abrufen des Benutzerkontexts',
        no_data_to_compare: 'Keine Daten zum Vergleichen',
        statistics: 'Statistiken',
        system_prompts: 'Systemaufforderungen',
        completion_tokens: 'Completion Tokens',
        prompt_tokens: 'Prompt-Token',
        all_tokens: 'Alle Token',
        run_time: 'Ausführungszeit',
        total_tokens: "Alle Tokens",
        prompt_id: 'Prompt-ID',
        dark_mode: 'Dunkelmodus',
        search_prompts: 'Prompts durchsuchen',
        open_account: 'Konto eröffnen',
        completion_content: 'Inhalt',
        close_comparison: 'Vergleich schließen',
        confirm_delete: 'Löschen bestätigen',
        delete_thread_confirmation: 'Sind Sie sicher, dass Sie diesen Thread löschen möchten?',
        cancel: 'Abbrechen',
        failed_to_delete_thread: 'Fehler beim Löschen des Threads',
        export_to_excel: "Für Excel exportieren",
        publish_social_media: "In sozialen Medien veröffentlichen",
        select_social_media: "Soziale Medien Konten auswählen",
        publish: "Veröffentlichen",
        provider: 'Anbieter',
        generate_image: 'Bild generieren',
        image_prompt: 'Geben Sie eine Bildbeschreibung ein...',
        group: 'Gruppe',
        open_context_manager: "Kontextmanager öffnen",
        hudinis_gripsbox: "Hudinis Gripsbox",
        upload_files: "Dateien hochladen",
        assign_tags: "Tags zuweisen",
        active: "Aktiv",
        close: "Schließen"

    },
    fr: {
        hudini_title: 'Hudini - Magicien du CPU sur SLM',
        select_model: 'Sélectionner le modèle',
        model: 'Modèle',
        select_category: 'Sélectionner une catégorie',
        select_category_placeholder: 'Sélectionnez une catégorie',
        enter_prompt: 'Entrez votre prompt ici...',
        send_button: 'Envoyer',
        delete: 'Supprimer',
        your_response: 'Votre réponse apparaîtra ici',
        copied_to_clipboard: 'Prompt copié dans le presse-papiers',
        failed_to_copy: 'Échec de la copie du prompt',
        prompt_deleted: 'Prompt supprimé',
        previous_prompts: 'Prompts Précédents',
        no_prompts: 'Aucun prompt enregistré',
        failed_to_prompts: 'Échec du chargement des prompts',
        select_model_placeholder: 'Sélectionnez un ou plusieurs modèles',
        local_models: 'Modèles Locaux',
        openai_models: 'Modèles OpenAI',
        invalid_prompt: 'Prompt invalide',
        prompt_saved: 'Prompt enregistré avec succès',
        failed_to_save_prompt: 'Échec de l\'enregistrement du prompt',
        failed_to_load_models: 'Échec du chargement des modèles',
        enter_prompt_and_select_model: 'Veuillez entrer un prompt et sélectionner au moins un modèle.',
        server_connection_error: 'Une erreur s\'est produite lors de la connexion au serveur.',
        select_category_and_model: 'Veuillez sélectionner une catégorie et un modèle',
        model_responses: 'Réponses du modèle',
        prompts: 'Prompts',
        models: 'Modèles',
        compare: 'Comparer',
        model_selection: 'Sélection de Modèle',
        prompt_submission: 'Soumission d\'Invite',
        content: 'Contenu',
        timestamp: 'Horodatage',
        error: 'Erreur',
        model_comparison: 'Comparaison de modèles',
        user_prompt: 'Invite de l\'utilisateur',
        no_error: 'Pas d\'erreur',
        copy_clipboard: 'Copier dans le presse-papiers',
        comparison_view: 'Vue de Comparaison',
        delete_thread: 'Supprimer le thread',
        delete_thread_confirmation_title: 'Êtes-vous sûr de vouloir supprimer ce fil de discussion ?',
        delete_thread_confirmation_content: 'Cette action est irréversible.',
        delete_thread_ok_text: 'Oui, supprimer',
        delete_thread_cancel_text: 'Non, garder',
        delete_thread_cancel_log: 'Suppression annulée',
        rerun_prompt: 'Relancer le Prompt',
        failed_to_retrieve_user_context: 'Échec de la récupération du contexte utilisateur',
        no_data_to_compare: 'Aucune donnée à comparer',
        statistics: 'Statistiques',
        system_prompts: 'Invites du système',
        completion_tokens: 'Jetons de Complétion',
        prompt_tokens: 'Jetons de Prompt',
        all_tokens: 'Tous les Jetons',
        run_time: 'Temps d\'Exécution',
        total_tokens: "Total des jetons",
        prompt_id: 'ID de l\'invite',
        dark_mode: 'Mode Sombre',
        search_prompts: 'Rechercher des prompts',
        open_account: 'Ouvrir un compte',
        completion_content: 'Contenu de Complétion',
        close_comparison: 'Fermer la Comparaison',
        confirm_delete: 'Confirmer la suppression',
        delete_thread_confirmation: 'Êtes-vous sûr de vouloir supprimer ce fil de discussion ?',
        cancel: 'Annuler',
        failed_to_delete_thread: 'Échec de la suppression du fil de discussion',
        export_to_excel: "Exporter vers Excel",
        publish_social_media: "Publier sur les réseaux sociaux",
        select_social_media: "Sélectionnez les comptes de réseaux sociaux",
        publish: "Publier",
        provider: 'Fournisseur',
        generate_image: 'Générer une image',
        image_prompt: 'Entrez une description d\'image...',
        group: 'Groupe',
        open_context_manager: "Ouvrir le gestionnaire de contexte",
        hudinis_gripsbox: "Boîte à astuces de Hudini",
        upload_files: "Télécharger des fichiers",
        assign_tags: "Attribuer des tags",
        active: "Actif",
        close: "Fermer"

    },
    ru: {
        hudini_title: 'Худини - Маг ЦП на SLM',
        select_model: 'Выберите модель',
        model: 'Модель',
        select_category: 'Выберите категорию',
        select_category_placeholder: 'Выберите категорию',
        enter_prompt: 'Введите ваш запрос здесь...',
        send_button: 'Отправить',
        delete: 'Удалить',
        your_response: 'Ваш ответ появится здесь',
        copied_to_clipboard: 'Подсказка скопирована в буфер обмена',
        failed_to_copy: 'Не удалось скопировать подсказку',
        prompt_deleted: 'Подсказка удалена',
        previous_prompts: 'Предыдущие подсказки',
        no_prompts: 'Пока нет сохраненных подсказок',
        failed_to_prompts: 'Не удалось загрузить подсказки',
        select_model_placeholder: 'Выберите одну или несколько моделей',
        local_models: 'Локальные модели',
        openai_models: 'Модели OpenAI',
        invalid_prompt: 'Недопустимый запрос',
        prompt_saved: 'Запрос успешно сохранен',
        failed_to_save_prompt: 'Не удалось сохранить запрос',
        failed_to_load_models: 'Не удалось загрузить модели',
        enter_prompt_and_select_model: 'Пожалуйста, введите запрос и выберите хотя бы одну модель.',
        server_connection_error: 'Произошла ошибка при подключении к серверу.',
        select_category_and_model: 'Пожалуйста, выберите категорию и модель',
        model_responses: 'Ответы модели',
        prompts: 'Запросы',
        models: 'Модели',
        compare: 'Сравнить',
        model_selection: 'Выбор модели',
        prompt_submission: 'Отправка запроса',
        content: 'Содержимое',
        timestamp: 'Временная метка',
        error: 'Ошибка',
        model_comparison: 'Сравнение моделей',
        user_prompt: 'Запрос пользователя',
        no_error: 'Нет ошибок',
        copy_clipboard: 'Копировать в буфер обмена',
        comparison_view: 'Просмотр сравнения',
        delete_thread: 'Удалить поток',
        delete_thread_confirmation_title: 'Вы уверены, что хотите удалить этот поток?',
        delete_thread_confirmation_content: 'Это действие невозможно отменить.',
        delete_thread_ok_text: 'Да, удалить',
        delete_thread_cancel_text: 'Нет, оставить',
        delete_thread_cancel_log: 'Удаление отменено',
        rerun_prompt: 'Повторить запрос',
        failed_to_retrieve_user_context: 'Не удалось получить контекст пользователя',
        no_data_to_compare: 'Нет данных для сравнения',
        statistics: 'Статистика',
        system_prompts: 'Системные подсказки',
        completion_tokens: 'Токены Завершения',
        prompt_tokens: 'Токены Запроса',
        all_tokens: 'Все Токены',
        run_time: 'Время Выполнения',
        total_tokens: "Всего токенов",
        prompt_id: 'ID запроса',
        dark_mode: 'Тёмный режим',
        search_prompts: 'Поиск подсказок',
        open_account: 'Открыть счет',
        completion_content: 'Содержание Завершения',
        close_comparison: 'Закрыть Сравнение',
        confirm_delete: 'Подтвердить удаление',
        delete_thread_confirmation: 'Вы уверены, что хотите удалить этот поток?',
        cancel: 'Отмена',
        failed_to_delete_thread: 'Не удалось удалить поток',
        export_to_excel: "Экспорт в Excel",
        publish_social_media: "Опубликовать в социальных сетях",
        select_social_media: "Выберите аккаунты социальных сетей",
        publish: "Опубликовать",
        provider: 'Поставщик',
        generate_image: '生成图片',
        image_prompt: '输入图片描述...',
        group: 'Группа',
        open_context_manager: "Открыть менеджер контекста",
        hudinis_gripsbox: "Коробка идей Худини",
        upload_files: "Загрузить файлы",
        assign_tags: "Назначить теги",
        active: "Активный",
        close: "Закрыть"
    },
    zh: {
        hudini_title: 'Hudini - CPU 魔术师在 SLM',
        select_model: '选择模型',
        model: '模型',
        select_category: '选择类别',
        select_category_placeholder: '选择一个类别',
        enter_prompt: '在此输入您的提示...',
        send_button: '发送',
        delete: '删除',
        your_response: '您的回应将在此处显示',
        copied_to_clipboard: '提示已复制到剪贴板',
        failed_to_copy: '无法复制提示',
        prompt_deleted: '提示已删除',
        previous_prompts: '之前的提示',
        no_prompts: '尚未保存任何提示',
        failed_to_prompts: '加载提示失败',
        select_model_placeholder: '选择一个或多个模型',
        local_models: '本地模型',
        openai_models: 'OpenAI 模型',
        invalid_prompt: '无效的提示',
        prompt_saved: '提示保存成功',
        failed_to_save_prompt: '保存提示失败',
        failed_to_load_models: '加载模型失败',
        enter_prompt_and_select_model: '请输入提示并选择至少一个模型。',
        server_connection_error: '连接服务器时发生错误。',
        select_category_and_model: '请选择类别和模型',
        model_responses: '模型响应',
        prompts: '提示',
        models: '模型',
        compare: '比较',
        model_selection: '模型选择',
        prompt_submission: '提示提交',
        content: '内容',
        timestamp: '时间戳',
        error: '错误',
        model_comparison: '模型比较',
        user_prompt: '用户提示',
        no_error: '没有错误',
        copy_clipboard: '复制到剪贴板',
        comparison_view: '比较视图',
        delete_thread: '删除线程',
        delete_thread_confirmation_title: '您确定要删除此线程吗？',
        delete_thread_confirmation_content: '此操作无法撤销。',
        delete_thread_ok_text: '是的，删除',
        delete_thread_cancel_text: '不，保留',
        delete_thread_cancel_log: '删除已取消',
        rerun_prompt: '重新运行提示',
        failed_to_retrieve_user_context: '无法检索用户上下文',
        no_data_to_compare: '没有数据可供比较',
        system_prompts: '系统提示',
        completion_tokens: '完成令牌',
        prompt_tokens: '提示令牌',
        all_tokens: '所有令牌',
        run_time: '运行时间',
        total_tokens: "代币总数", prompt_id: '提示 ID',
        dark_mode: '暗黑模式',
        search_prompts: '搜索提示',
        open_account: '开立账户',
        completion_content: '完成内容',
        close_comparison: '关闭比较',
        confirm_delete: '确认删除',
        delete_thread_confirmation: '您确定要删除此线程吗？',
        cancel: '取消',
        failed_to_delete_thread: '删除线程失败',
        export_to_excel: "导出到 Excel",
        publish_social_media: "发布到社交媒体",
        select_social_media: "选择社交媒体账户",
        publish: "发布",
        provider: '供应商',
        generate_image: '生成图片',
        image_prompt: '输入图片描述...',
        group: '组',
        open_context_manager: "打开上下文管理器",
        hudinis_gripsbox: "胡迪尼的智慧盒",
        upload_files: "上传文件",
        assign_tags: "分配标签",
        active: "激活",
        close: "关闭"
    },
    // Add other languages as needed
};


const i18n = createI18n({
    legacy: false,
    locale: localStorage.getItem('locale') || 'de',
    fallbackLocale: 'en',
    messages,
});

export default i18n;
