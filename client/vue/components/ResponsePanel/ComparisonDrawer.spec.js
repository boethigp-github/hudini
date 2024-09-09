import { mount } from '@vue/test-utils';
import { describe, it, expect, vi } from 'vitest';
import ComparisonDrawer from './ComparisonTable.vue';
import { createI18n } from 'vue-i18n';


// Create a basic i18n setup (if needed for your component)
const messages = {
    en: {
        no_data: 'No data to compare.',
    },
};

const i18n = createI18n({
    legacy: false,
    locale: 'en',
    fallbackLocale: 'en',
    messages,
});

describe('ComparisonTable.vue', () => {

    const plugins = [];  // Add any plugins needed for Markdown rendering

    it('renders the drawer with the correct title', () => {
        const wrapper = mount(ComparisonDrawer, {
            props: {
                comparisonData: [],
                plugins: plugins,
                width: '500px',
            },
            global: {
                plugins: [i18n],
            },
        });

        wrapper.vm.drawerVisible = true;  // Simulate drawer being open

        // Check if the string "Response Comparison" is present in the HTML
        expect(wrapper.html()!=='');
    });

    it('displays "No data to compare." when comparisonData is empty', () => {
        const wrapper = mount(ComparisonDrawer, {
            props: {
                comparisonData: [],
                plugins: plugins,
                width: '500px',
            },
            global: {
                plugins: [i18n],
            },
        });



        expect(wrapper.html()!=='');
    });

    it('renders comparison table with data correctly', () => {
        const mockData = [
            {
                model: 'gpt-3.5-turbo',
                content: 'The weather is sunny with a high of 25°C.',
                timestamp: '2023-08-25 12:34:56',
                error: '',
            },
            {
                model: 'gpt-4',
                content: 'Expect rain in the evening.',
                timestamp: '2023-08-25 12:35:56',
                error: '',
            }
        ];

        const wrapper = mount(ComparisonDrawer, {
            props: {
                comparisonData: mockData,
                plugins: plugins,
                width: '500px',
            },
            global: {
                plugins: [i18n],
            },
        });


        expect(wrapper.html()!=='');
    });

    it('renders markdown content using VueMarkdownIT', () => {
        const mockData = [
            {
                model: 'gpt-3.5-turbo',
                content: '**Bold Text** and *italic*',
                timestamp: '2023-08-25 12:34:56',
                error: '',
            }
        ];

        const wrapper = mount(ComparisonDrawer, {
            props: {
                comparisonData: mockData,
                plugins: plugins,
                width: '500px',
            },
            global: {
                plugins: [i18n],
            },
        });

        expect(wrapper.html() !=='');

    });

    it('handles closeDrawer event correctly', async () => {
        const wrapper = mount(ComparisonDrawer, {
            props: {
                comparisonData: [],
                plugins: plugins,
                width: '500px',
            },
            global: {
                plugins: [i18n],
            },
        });

        const closeDrawerSpy = vi.spyOn(wrapper.vm, 'closeDrawer');
        await wrapper.vm.closeDrawer();

        expect(closeDrawerSpy).toHaveBeenCalled();
        expect(wrapper.vm.drawerVisible).toBe(false);
    });
});
