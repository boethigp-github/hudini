<template>
    <div id="response" class="response">
        <div v-if="!response" class="placeholder">
            {{ $t('your_response') }}
        </div>
        <div>{{ response }}</div>
    </div>
</template>

<script>
export default {
    name: 'ResponsePanel',
    props: {
        response: {
            type: String,
            required: true,
        }
    },
    methods: {
        scrollToBottom() {
            const responseElement = this.$el;
            responseElement.scrollTop = responseElement.scrollHeight;
        }
    },
    watch: {
        response() {
            this.scrollToBottom();
        }
    }
};
</script>

<style scoped>
/* Add your styles here */
.response {
    max-height: 400px; /* or any other value */
    overflow-y: auto;
    padding: 10px;
    border: 1px solid #ddd;
}

.placeholder {
    color: #aaa;
}
</style>
