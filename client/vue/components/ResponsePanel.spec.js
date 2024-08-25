import { mount } from '@vue/test-utils';
import { describe, it, expect } from 'vitest';
import { createI18n } from 'vue-i18n';
import ResponsePanel from './ResponsePanel.vue';

// Create a basic i18n setup
const messages = {
    en: {
        your_response: 'Your response will appear here',
        model: 'Model',
    },
};

const i18n = createI18n({
    legacy: false,
    locale: 'en',
    fallbackLocale: 'en',
    messages,
});

describe('ResponsePanel.vue', () => {


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
                loading: false,
                drawerVisible: false,
            },
            global: {
                plugins: [i18n],
            },
        });

        expect(wrapper.find('.response-item').exists()).toBe(true);
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
                loading: false,
                drawerVisible: false,
            },
            global: {
                plugins: [i18n],
            },
        });

        expect(wrapper.find('.incomplete-item').exists()).toBe(true);

    });


    it('does not display loading skeleton when loading is false', () => {
        const wrapper = mount(ResponsePanel, {
            props: { responses: [], loading: false, drawerVisible: false },
            global: {
                plugins: [i18n],
            },
        });

        expect(wrapper.find('a-skeleton').exists()).toBe(false);
    });

    it('renders the prompt correctly when there is a mocked response', () => {
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
                loading: false,
                drawerVisible: false,
            },
            global: {
                plugins: [i18n],
            },
        });

        // Check if the prompt is rendered correctly
        expect(wrapper.find('.prompt-text').text()).toBe('What is the weather like today?');
    });


    it('renders a response correctly', () => {
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
                loading: false,
                drawerVisible: false,
            },
            global: {
                plugins: [i18n],
            },
        });

        // Check if the response content is rendered correctly
        const responseItem = wrapper.find('.response-item');
        expect(responseItem.exists()).toBe(true);
        //expect(wrapper.find('.response-content').text()).toContain('The weather is sunny with a high of 25°C.');
    });



});
