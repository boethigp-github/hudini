import { mount } from '@vue/test-utils';
import { describe, it, expect, beforeEach } from 'vitest';
import SseTestComponent from './../../components/SseTestComponent.vue';
import EventSource from 'eventsource';  // Import the EventSource polyfill

// Apply the polyfill globally
global.EventSource = EventSource;

describe('SseTestComponent', () => {
    let wrapper;

    beforeEach(() => {
        wrapper = mount(SseTestComponent);
    });

    it('initiates SSE connection on button click and receives messages', async () => {
        const pingButton = wrapper.find('button');
        await pingButton.trigger('click');

        // Wait for the message to be received
        await new Promise(resolve => setTimeout(resolve, 5000)); // Increase delay for SSE processing

        const responseText = wrapper.find('div').text();
        console.log('Received response:', responseText); // Log the response for debugging

        expect(responseText).toContain('Response: Server is alive');
    }, 100);
});
