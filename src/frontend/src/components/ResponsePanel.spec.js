import { mount } from '@vue/test-utils';
import { describe, it, expect, vi } from 'vitest';
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
            props: { responses: [], currentResponse: '' },
            global: {
                plugins: [i18n],
            },
        });

        expect(wrapper.find('.placeholder').exists()).toBe(true);
        expect(wrapper.text()).toContain('Your response will appear here'); // Ensure this matches the i18n message
    });

    it('renders the response correctly', async () => {
        const wrapper = mount(ResponsePanel, {
            props: { responses: [], currentResponse: 'This is a test response' },
            global: {
                plugins: [i18n],
            },
        });

        expect(wrapper.find('.placeholder').exists()).toBe(false);
        expect(wrapper.find('.current-response').text()).toBe('This is a test response');
    });

    it('calls scrollToBottom when response changes', async () => {
        const wrapper = mount(ResponsePanel, {
            props: { responses: [], currentResponse: 'Initial response' },
            global: {
                plugins: [i18n],
            },
        });

        const scrollToBottomSpy = vi.spyOn(wrapper.vm, 'scrollToBottom');
        await wrapper.setProps({ responses: [], currentResponse: 'Updated response' });

        expect(scrollToBottomSpy).toHaveBeenCalled();
    });

    it('scrolls to bottom when response changes', async () => {
        const wrapper = mount(ResponsePanel, {
            props: { responses: [], currentResponse: 'Initial response' },
            global: {
                plugins: [i18n],
            },
        });

        // Mock scrollTop and scrollHeight properties
        const responseElement = wrapper.find('#response').element;

        Object.defineProperty(responseElement, 'scrollTop', {
            writable: true,
            value: 0,
        });
        Object.defineProperty(responseElement, 'scrollHeight', {
            writable: true,
            value: 100,
        });

        await wrapper.setProps({ currentResponse: 'New response' });

        // Wait for the next DOM update
        await wrapper.vm.$nextTick();

        // Verify the scrollTop value is updated
        expect(responseElement.scrollTop).toBe(responseElement.scrollHeight);
    });
});
