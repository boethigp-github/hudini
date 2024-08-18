import { mount } from '@vue/test-utils';
import { describe, it, expect } from 'vitest';
import { createI18n } from 'vue-i18n';
import ResponsePanel from './ResponsePanel.vue';

// Create a basic i18n setup
const messages = {
    en: {
        your_response: 'Your response will appear here',
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
        expect(wrapper.text()).toContain('Your response will appear here');
    });

    it('renders completed responses correctly', () => {
        const wrapper = mount(ResponsePanel, {
            props: {
                responses: [
                    {
                        status: 'complete',
                        token: 'This is a completed response',
                        timestamp: '2024-08-18 14:00:00',
                        model: 'gpt-3.5-turbo',
                    },
                ],
            },
            global: {
                plugins: [i18n],
            },
        });

        expect(wrapper.find('.response-item').exists()).toBe(true);
        expect(wrapper.find('.response-item .response-content').text()).toBe('This is a completed response');
        expect(wrapper.find('.response-item .timestamp').text()).toBe('2024-08-18 14:00:00');
        expect(wrapper.find('.response-item .model').text()).toBe('gpt-3.5-turbo');
    });

    it('renders incomplete responses correctly', () => {
        const wrapper = mount(ResponsePanel, {
            props: {
                responses: [
                    {
                        status: 'incomplete',
                        token: 'This is an incomplete response',
                        timestamp: '2024-08-18 14:00:00',
                        model: 'gpt-3.5-turbo',
                    },
                ],
            },
            global: {
                plugins: [i18n],
            },
        });

        expect(wrapper.find('.incomplete-item').exists()).toBe(true);
        expect(wrapper.find('.incomplete-item .response-content').text()).toBe('This is an incomplete response');
    });



});
