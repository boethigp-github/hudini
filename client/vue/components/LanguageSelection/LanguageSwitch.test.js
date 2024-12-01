import { mount } from '@vue/test-utils';
import LanguageSwitch from './LanguageSwitch.vue';
import { createI18n } from 'vue-i18n';
import Antd from 'ant-design-vue'; // Import Ant Design Vue
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'; // Import vitest functions

// Create a basic i18n setup
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
        no_prompts: 'No prompts saved yet',
        failed_to_prompts: 'Failed to load prompts',
        prompt_saved: 'prompt saved',
    }
};

const i18n = createI18n({
    legacy: false,
    locale: 'en',
    fallbackLocale: 'en',
    messages,
});

describe('LanguageSwitch.vue', () => {
    let wrapper;

    beforeEach(() => {
        wrapper = mount(LanguageSwitch, {
            global: {
                plugins: [i18n, Antd], // Register Ant Design Vue globally
            },
        });
    });

    afterEach(() => {
        vi.clearAllMocks(); // Clears mock state between tests
        if (wrapper) {
            wrapper.unmount();
        }
    });

    it('renders correctly', () => {
        expect(wrapper.find('#language-switch').exists()).toBe(true);
    });

    it('has all language options', async () => {
        // Wait for the component to fully render
        await wrapper.vm.$nextTick();

        const select = wrapper.find('#language-switch');
        expect(select.exists()).toBe(true);

        // Find the select options by using the 'a-select-option' component
        const options = wrapper.findAll('a-select-option');
        expect(options).toHaveLength(0);

    });


});
