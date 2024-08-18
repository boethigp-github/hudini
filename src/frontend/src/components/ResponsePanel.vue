<!--suppress CssUnusedSymbol -->
<template>
    <div id="response" class="response">
        <!-- Render the list of responses -->
        <div v-for="(item, index) in responses"
            :key="index"
            :class="[item.status === 'complete' ? 'response-item' : 'incomplete-item']"
        >
            <div v-if="item.token?.trim().length">
                <div class="response-metadata">
                    <span class="timestamp">{{ item.timestamp }}</span>
                    <span class="model">{{ item.model }}</span>
                </div>
                <div class="response-content">
                    {{ item.token }}
                </div>
            </div>
        </div>

        <!-- Placeholder message if no responses are present -->
        <div v-if="responses.length === 0" class="placeholder">
            {{ $t('your_response') }}
        </div>
    </div>
</template>

<script>
import { nextTick, watch } from 'vue';

export default {
    name: 'ResponsePanel',
    props: {
        responses: {
            type: Array,
            required: true,
            default: () => [],
        },
    },
    setup(props) {
        const scrollToBottom = () => {
            nextTick(() => {
                const responseElement = document.getElementById('response');
                responseElement.scrollTop = responseElement.scrollHeight;
            });
        };

        watch(
            () => props.responses,
            () => {
                scrollToBottom();
            },
            { deep: true } // Ensure deep watching of the array's content
        );

        return {
            scrollToBottom,
        };
    }
};
</script>

<style scoped>
.response {
    max-height: 54vh;
    height: 54vh;
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

.incomplete-item {
    border: none;
    margin-top: 10px;
    border: #4CAF50;
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

.placeholder {
    color: #aaa;
}
</style>
