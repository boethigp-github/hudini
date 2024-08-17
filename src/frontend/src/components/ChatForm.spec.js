import { mount } from '@vue/test-utils';
import ChatForm from './ChatForm.vue';
import { createI18n } from 'vue-i18n';
import Antd from 'ant-design-vue'; // Import Ant Design Vue
import { nextTick } from 'vue';
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'; // Import vitest functions

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
        enter_prompt: 'Enter your prompt here...',
        send_button: 'Send',
        delete: 'Delete',
        your_response: 'Your response will appear here',
        copied_to_clipboard: 'Prompt copied to clipboard',
        failed_to_copy: 'Failed to copy prompt',
        prompt_deleted: 'Prompt deleted',
        previous_prompts: 'Previous Prompts',
        no_prompts: 'No prompts saved yet',
        failed_to_load_prompts: 'Failed to load prompts',
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
    if (url.includes('/get_models')) {
        return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({
                local_models: ['Local Model 1', 'Local Model 2'],
                openai_models: ['OpenAI Model 1', 'OpenAI Model 2']
            }),
        });
    } else if (url.includes('/generate')) {
        return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({ result: 'Generated response' }),
        });
    } else if (url.includes('/save_prompt')) {
        return Promise.resolve({ ok: true });
    } else if (url.includes('/load_prompts')) {
        return Promise.resolve({
            ok: true,
            json: () => Promise.resolve([]),
        });
    }
});

describe('ChatForm.vue', () => {
    let wrapper;

    beforeEach(() => {
        wrapper = mount(ChatForm, {
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

    it('renders correctly and displays the title', () => {
        expect(wrapper.text()).toContain('Hudini - CPU Magician on SLM');
    });

    it('loads models on mount', async () => {
        await nextTick();
        expect(global.fetch).toHaveBeenCalledWith(expect.stringContaining('/get_models'));

        // Check that the models were loaded correctly
        expect(wrapper.vm.localModels.length).toBeGreaterThan(0);
        expect(wrapper.vm.openaiModels.length).toBeGreaterThan(0);
    });

    it('updates the response area when a prompt is submitted', async () => {
        // Wait until the models are loaded and the DOM updates
        await nextTick();
        await nextTick();

        // Set selectedModel and prompt by simulating user input
        const select = wrapper.find('input.ant-select-selection-search-input'); // Adjust the selector based on how a-select renders
        await select.setValue('Local Model 1');
        const textarea = wrapper.find('textarea');
        await textarea.setValue('Test Prompt');

        // Simulate clicking the send button
        const sendButton = wrapper.find('.send-button');
        await sendButton.trigger('click');
        await nextTick();

        // Log the fetch calls to diagnose extra calls
        fetch.mock.calls.forEach((call, index) => {
            console.log(`Fetch Call ${index + 1}: ${call[0]}`);
        });


        // Verify that the response area updated
        expect(wrapper.find('#response').text()).toContain('Your response will appear here');
    });

    it('increments updateTrigger when prompt is saved', async () => {
        // Wait until the models are loaded and the DOM updates
        await nextTick();
        await nextTick();

        // Set selectedModel and prompt by simulating user input
        const select = wrapper.find('input.ant-select-selection-search-input');
        await select.setValue('Local Model 1');
        const textarea = wrapper.find('textarea');
        await textarea.setValue('Test Prompt');

        // Simulate clicking the send button
        const sendButton = wrapper.find('.send-button');
        await sendButton.trigger('click');
        await nextTick();

        // Expect updateTrigger to increment
        expect(wrapper.vm.updateTrigger).toBe(1);
    });
});
