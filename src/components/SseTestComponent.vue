<template>
    <div>
        <input v-model="prompt" type="text" placeholder="Enter prompt" />
        <button @click="handleSubmit" :disabled="loading">SSE Check</button>
        <div>Response: {{ response }}</div>
    </div>
</template>

<script>
import { ref } from 'vue';

export default {
    name: 'SseTestComponent',
    setup() {
        const prompt = ref('');
        const response = ref('');
        const loading = ref(false);
        const serverUrl = import.meta.env.VITE_SERVER_URL || 'http://localhost:5000';

        const handleSubmit = () => {
            // You can remove the prompt check here since it's not needed for /ping
            loading.value = true;
            response.value = '';

            try {
                // Connect directly to the /ping endpoint using EventSource
                const eventSource = new EventSource(`http://localhost:5000/ping`);

                eventSource.onmessage = (event) => {
                    if (event.data === '[END]') {
                        eventSource.close();
                        loading.value = false;
                    } else {
                        response.value += event.data + ' ';
                    }
                };

                eventSource.onerror = (error) => {
                    console.error('EventSource failed:', error);
                    response.value = 'An error occurred while processing your request.';
                    eventSource.close();
                    loading.value = false;
                };
            } catch (error) {
                console.error('There was an error:', error);
                response.value = 'An error occurred while processing your request.';
                loading.value = false;
            }
        };

        return {
            prompt,
            response,
            loading,
            handleSubmit,
        };
    },
};
</script>
