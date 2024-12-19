import { mount } from '@vue/test-utils';
import PromptPanel from './PromptPanel.vue';
import { createI18n } from 'vue-i18n';
import { nextTick } from 'vue';



const messages = {
    en: {
        delete: 'Delete',
        prompt_deleted: 'Prompt deleted',
    },
    de: {
        delete: 'Delete',
        prompt_deleted: 'Prompt deleted',
    }
};

const i18n = createI18n({
    legacy: false,
    locale: localStorage.getItem('locale') || 'de',
    fallbackLocale: 'en',
    messages,
});

export default i18n;

// Create an i18n instance
// Mock the fetch API globally
global.fetch = vi.fn(() =>
    Promise.resolve({
        ok: true,
        json: () => Promise.resolve([
            {
                id: '1',
                prompt: 'First prompt',
                timestamp: Date.now(),
            },
            {
                id: '2',
                prompt: 'Second prompt',
                timestamp: Date.now(),
            },
        ]),
    })
);

describe('PromptPanel.vue', () => {
    let wrapper;

    beforeEach(() => {
        wrapper = mount(PromptPanel, {
            global: {
                plugins: [i18n],
            },
        });
    });

    afterEach(() => {
        if (wrapper) {
            wrapper.unmount();
        }
    });

    it('should load and display prompts correctly', async () => {
        // Wait for the fetch to resolve and the DOM to update
        await nextTick();
        await nextTick();

        // Access the previousPrompts state directly
        const previousPrompts = wrapper.vm.previousPrompts;

        // Check if the prompts are loaded and displayed
        expect(previousPrompts.length).toBe(2);
        expect(previousPrompts[0].prompt).toContain('First prompt');
        expect(previousPrompts[1].prompt).toContain('Second prompt');
    });

    it('should delete a prompt and update previousPrompts state', async () => {
        // Mock the delete API
        fetch.mockImplementationOnce(() =>
            Promise.resolve({
                ok: true,
                json: () => Promise.resolve([]), // Return an empty array to simulate deletion
            })
        );

        // Wait for the fetch to resolve and the DOM to update
        await nextTick();
        await nextTick();

        // Simulate clicking the delete button for the first prompt
        const deleteButton = wrapper.findAll('.delete-button').at(0);
        await deleteButton.trigger('click');
    });
});
