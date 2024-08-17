import { defineConfig, loadEnv } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig(({ mode }) => {
    const env = loadEnv(mode, process.cwd(), '');

    return {
        plugins: [vue()],
        test: {
            globals: true,
            environment: 'jsdom',
            setupFiles: ['./vitest.setup.js'],
            testTimeout: 10000,
            coverage: {
                provider: 'v8',
                reporter: ['text', 'json', 'html'],
            },
        },
        resolve: {
            alias: {
                '@': '/frontend/src', // '@' now correctly points to 'frontend/src' directory
            },
        },
        define: {
            'import.meta.env.VITE_SERVER_URL': JSON.stringify(env.SERVER_URL),
        },
    };
});
