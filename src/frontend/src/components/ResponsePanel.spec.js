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
            props: { responses: [], currentResponse: null },
            global: {
                plugins: [i18n],
            },
        });

        expect(wrapper.find('.placeholder').exists()).toBe(true);
        expect(wrapper.text()).toContain('Your response will appear here');
    });

    it('renders the current response correctly', async () => {
        const wrapper = mount(ResponsePanel, {
            props: { responses: [], currentResponse: { token: 'This is a test response', timestamp: '2024-08-18 14:00:00', model: 'gpt-3.5-turbo' } },
            global: {
                plugins: [i18n],
            },
        });

        expect(wrapper.find('.placeholder').exists()).toBe(false);
        expect(wrapper.find('.current-response .response-content').text()).toBe('This is a test response');
        expect(wrapper.find('.current-response .timestamp').text()).toBe('2024-08-18 14:00:00');
        expect(wrapper.find('.current-response .model').text()).toBe('gpt-3.5-turbo');
    });

    it('renders completed responses correctly', async () => {
        const wrapper = mount(ResponsePanel, {
            props: {
                responses: [
                    { status: 'complete', token: 'This is a completed response', timestamp: '2024-08-18 14:00:00', model: 'gpt-3.5-turbo' },
                ],
                currentResponse: null,
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



    it('calls scrollToBottom when responses change', async () => {
        const wrapper = mount(ResponsePanel, {
            props: { responses: [], currentResponse: null },
            global: {
                plugins: [i18n],
            },
        });

        const scrollToBottomSpy = vi.spyOn(wrapper.vm, 'scrollToBottom');
        await wrapper.setProps({
            responses: [
                { status: 'complete', token: 'This is a new response', timestamp: '2024-08-18 14:00:00', model: 'gpt-3.5-turbo' },
            ],
        });

        expect(scrollToBottomSpy).toHaveBeenCalled();
    });

    it('scrolls to bottom when current response changes', async () => {
        const wrapper = mount(ResponsePanel, {
            props: { responses: [], currentResponse: { token: 'Initial response', timestamp: '2024-08-18 14:00:00', model: 'gpt-3.5-turbo' } },
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

        await wrapper.setProps({ currentResponse: { token: 'New response', timestamp: '2024-08-18 14:05:00', model: 'gpt-3.5-turbo' } });

        await wrapper.vm.$nextTick();

        expect(responseElement.scrollTop).toBe(responseElement.scrollHeight);
    });
});
