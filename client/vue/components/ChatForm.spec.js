import { mount } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import ChatForm from './ChatForm.vue';
import { createI18n } from 'vue-i18n';
import Antd from 'ant-design-vue';
import { nextTick } from 'vue';
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { useModelsStore } from './../stores/models';

// Mock window.matchMedia
window.matchMedia = window.matchMedia || function () {
    return {
        matches: false,
        addListener: function () { },
        removeListener: function () { }
    };
};

// Mock EventSource
global.EventSource = vi.fn(() => ({
    onmessage: null,
    onerror: null,
    close: vi.fn(),
}));

// Create a basic i18n setup
const messages = {
    en: {
        hudini_title: 'Hudini - CPU Magician on SLM',
        select_model: 'Select Model',
        select_model_placeholder: 'Select one or more models',
        local_models: 'Local Models',
        openai_models: 'OpenAI Models',
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
        server_connection_error: 'Server connection error',
        failed_to_save_prompt: 'Failed to save prompt',
        prompt_saved: 'Prompt saved',
        select_category: 'Select Category', // Added key
        select_category_placeholder: 'Select a category...', // Added key
        model_responses: 'Model Responses', // Added key
        prompts: 'Prompts', // Added key
        select_category_and_model: 'select_category_and_model', // Added key
        models: 'models', // Added key
    }
};

const i18n = createI18n({
    legacy: false,
    locale: 'en',
    fallbackLocale: 'en',
    messages,
});

// Mock the fetch API globally
global.fetch = vi.fn((url) => {
    if (url.includes('/models')) {
        return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({
                local_models: ['Local Model 1', 'Local Model 2'],
                openai_models: ['OpenAI Model 1', 'OpenAI Model 2']
            }),
        });

    } else if (url.includes('/prompts')) {
        return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({ status: 'success' }),
        });
    } else if (url.includes('/stream')) {
        return Promise.resolve({
            ok: true,
            body: {
                getReader: () => ({
                    read: async () => ({
                        done: true,
                        value: new TextEncoder().encode(
                            JSON.stringify({
                                status: 'data',
                                token: 'Test token',
                                data: 'Test data',
                                timestamp: '2024-08-18 12:22:51',
                                user: 1234, // Changed to integer
                                prompt: 'Tell me a short joke',
                                id: 5678, // Changed to integer
                                model: 'gpt-3.5-turbo',
                            })
                        ),
                    }),
                }),
            },
        });
    } else if (url.includes('/prompts')) {
        return Promise.resolve({
            ok: true,
            json: () => Promise.resolve([]),
        });
    }
});

describe('ChatForm.vue', () => {
    let wrapper;

    beforeEach(async () => {
        const pinia = createPinia();
        setActivePinia(pinia);

        // Create the store and initialize with data
        const modelsStore = useModelsStore();
        await modelsStore.setSelectedModels(['Local Model 1', 'OpenAI Model 1']); // Use the existing action to set models

        wrapper = mount(ChatForm, {
            global: {
                plugins: [pinia, i18n, Antd],
            },
        });

        // Ensure models are loaded
        await nextTick();
    });

    afterEach(() => {
        vi.clearAllMocks();
        if (wrapper) {
            wrapper.unmount();
        }
    });

    it('checks if the model select box is available', () => {
        const selectBox = wrapper.findComponent({ name: 'ModelSelection' });
        expect(selectBox.exists()).toBe(true);
    });

    it('checks if the language switch is available', () => {
        const languageSwitch = wrapper.findComponent({ name: 'LanguageSwitch' });
        expect(languageSwitch.exists()).toBe(true);
    });

    it('checks if the logo is available', () => {
        const logo = wrapper.find('img.logo');
        expect(logo.exists()).toBe(true);
        expect(logo.attributes('alt')).toBe('Hudini Logo');
    });

    it('checks if the response panel is available', () => {
        const responsePanel = wrapper.findComponent({ name: 'ResponsePanel' });
        expect(responsePanel.exists()).toBe(true);
    });

    it('checks if the previous prompts panel is available', () => {
        const promptPanel = wrapper.findComponent({ name: 'PromptPanel' });
        expect(promptPanel.exists()).toBe(true);
    });
});
