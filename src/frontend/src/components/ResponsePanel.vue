<template>
    <div id="response" class="response">
        <!-- Render the list of completed responses in reverse order -->
        <div v-for="(item, index) in reversedResponses" :key="index" class="response-item">
            {{ item }}
        </div>

        <!-- Render the current response at the bottom -->
        <div v-if="currentResponse" class="response-item current-response">
            {{ currentResponse }}
        </div>

        <!-- Placeholder message if no responses are present -->
        <div v-if="responses.length === 0 && !currentResponse" class="placeholder">
            {{ $t('your_response') }}
        </div>
    </div>
</template>

<script>
export default {
    name: 'ResponsePanel',
    props: {
        responses: {
            type: Array,
            required: true,
            default: () => [],
        },
        currentResponse: {
            type: String,
            default: '',
        },
    },
    computed: {
        reversedResponses() {
            // Reverse the responses to display the latest at the bottom
            return [...this.responses];
        }
    },
    methods: {
        scrollToBottom() {
            this.$nextTick(() => {
                const responseElement = this.$el;
                responseElement.scrollTop = responseElement.scrollHeight;
            });
        }
    },
    watch: {
        responses() {
            this.scrollToBottom();
        },
        currentResponse() {
            this.scrollToBottom();
        }
    }
};
</script>

<style scoped>
.response {
    max-height: 50vh; /* Max height as 60% of the viewport height */
    overflow-y: auto; /* Enable vertical scrolling if content exceeds max height */
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 5px;
    background-color: #f9f9f9;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    display: flex;
    flex-direction: column; /* Ensure new text appears at the bottom */
}

.placeholder {
    color: #aaa;
}

.response-item {
    border: 2px solid #4CAF50; /* Customize border color */
    border-radius: 10px; /* Rounded corners */
    padding: 10px;
    background-color: #f9f9f9; /* Light background color */
    margin-top: 10px; /* Space between items */
}

.current-response {
    border: 2px solid #2196F3; /* Different color for current response */
    background-color: #e3f2fd; /* Light background color for current response */
}
</style>
