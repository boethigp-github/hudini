import { mount } from '@vue/test-utils';
import { describe, it, expect } from 'vitest';
import { createI18n } from 'vue-i18n';
import ResponsePanel from './ResponsePanel.vue';

// Create a basic i18n setup
const messages = {
    en: {
        your_response: 'Your response will appear here',
        model: 'Model'
    },
};

const i18n = createI18n({
    legacy: false,
    locale: 'en',
    fallbackLocale: 'en',
    messages,
});

describe('ResponsePanel.vue', () => {
    it('renders correctly with an empty response', () => {
        const wrapper = mount(ResponsePanel, {
            props: { responses: [] },
            global: {
                plugins: [i18n],
            },
        });

        expect(wrapper.find('.placeholder').exists()).toBe(true);

    });

    it('renders completed responses correctly', () => {
        const wrapper = mount(ResponsePanel, {
            props: {
                responses: [
                    {
                        status: 'complete',
                        prompt: 'What is the weather like today?',
                        completion: {
                            created: 1724001600,  // Assuming this is a UNIX timestamp
                            choices: [
                                {
                                    message: {
                                        content: 'The weather is sunny with a high of 25°C.'
                                    }
                                }
                            ]
                        },
                        model: 'gpt-3.5-turbo',
                    },
                ],
            },
            global: {
                plugins: [i18n],
            },
        });

        expect(wrapper.find('.response-item').exists()).toBe(true);
        expect(wrapper.find('.response-content').text()).toBe('The weather is sunny with a high of 25°C.');

        expect(wrapper.find('.model').text()).toBe('Model: gpt-3.5-turbo');
    });

    it('renders incomplete responses correctly', () => {
        const wrapper = mount(ResponsePanel, {
            props: {
                responses: [
                    {
                        status: 'incomplete',
                        prompt: 'Tell me a joke.',
                        error: 'Response not available.',
                        model: 'gpt-3.5-turbo',
                    },
                ],
            },
            global: {
                plugins: [i18n],
            },
        });

        expect(wrapper.find('.incomplete-item').exists()).toBe(true);
        expect(wrapper.find('.response-content').text()).toBe('Response not available.');
    });
});
