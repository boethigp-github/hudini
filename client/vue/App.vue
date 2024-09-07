<template>
    <div id="app">
        <a-config-provider :theme="{ token: { colorPrimary: '#939393' } }">
        <ChatForm />
        </a-config-provider>
    </div>
</template>

<script>
import ChatForm from './components/ChatForm.vue';

export default {
    components: {
        ChatForm,
    },
};
</script>

<style>
/* Add any global styles here */
</style>
