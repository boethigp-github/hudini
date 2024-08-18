<!--suppress CssUnusedSymbol -->
<template>
    <div id="response" class="response">
        <div v-for="(item, index) in displayedResponses" :key="index" :class="[item.status === 'complete' ? 'response-item' : 'incomplete-item']">
            <div v-if="item.status === 'complete' && item.token?.trim().length">
                <div class="response-metadata">
                    <span class="timestamp">{{ item.timestamp }}</span>
                    <span class="model">{{ item.model }}</span>
                </div>
                <div class="response-content">
                    {{ item.token }}
                </div>
            </div>
        </div>

        <!-- Render the current response at the bottom -->
        <div v-if="currentResponse?.token?.trim().length" class="response-item current-response">
            <div class="response-metadata">
                <span class="timestamp">{{ currentResponse.timestamp }}</span>
                <span class="model">{{ currentResponse.model }}</span>
            </div>
            <div class="response-content">
                {{ currentResponse.token }}
            </div>
        </div>

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
            type: Object,
            default: () => null,
        },
    },
    data() {
        return {
            reversed: false, // Track if the responses are reversed
        };
    },
    computed: {
        displayedResponses() {
            // Reverse the responses only if they have been reversed already
            return this.responses;
        },
    },
    methods: {
        scrollToBottom() {
            this.$nextTick(() => {
                const responseElement = this.$el;
                responseElement.scrollTop = responseElement.scrollHeight;
            });
        },
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
    max-height: 50vh;
    overflow-y: auto;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 5px;
    background-color: #f9f9f9;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    display: flex;
    flex-direction: column;
}

.response-item {
    border: 2px solid #4CAF50;
    border-radius: 10px;
    padding: 10px;
    background-color: #f9f9f9;
    margin-top: 10px;
}

.response-metadata {
    display: flex;
    justify-content: space-between;
    margin-bottom: 5px;
    color: #666;
    font-size: 0.875rem;
}

.timestamp {
    font-size: 12px;
    color: #666;
}

.model {
    color: #999;
    font-weight: bold;
    margin-top: -5px;
}

.response-content {
    font-size: 0.9rem;
    color: #333;
}

.current-response {
    border: 2px solid #2196F3;
    background-color: #e3f2fd;
}

.placeholder {
    color: #aaa;
}

.incomplete-item{
    border: none;
}
</style>
