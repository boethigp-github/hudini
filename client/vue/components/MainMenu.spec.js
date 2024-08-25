import { mount } from '@vue/test-utils';
import { describe, it, expect, vi } from 'vitest';
import ChatMenu from './MainMenu.vue';
import { createI18n } from 'vue-i18n';
import { Menu } from 'ant-design-vue';

// Create a basic i18n setup (if needed for your component)
const messages = {
    en: {
        model_responses: 'Model Responses',
        compare: 'Compare',
        prompts: 'Prompts',
        system_prompts: 'System Prompts',
    },
};

const i18n = createI18n({
    legacy: false,
    locale: 'en',
    fallbackLocale: 'en',
    messages,
});

describe('ChatMenu.vue', () => {

    it('renders the menu with correct items and icons', () => {
        const wrapper = mount(ChatMenu, {
            global: {
                plugins: [i18n],
            },
        });

        // Check the existence of menu titles
        expect(wrapper.html()).toContain('ant-menu');
        expect(wrapper.html()).toContain('ant-menu-title-content');

    });



});
