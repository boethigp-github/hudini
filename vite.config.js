import { defineConfig, loadEnv } from 'vite';
import vue from '@vitejs/plugin-vue';

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
    // Load env file based on `mode` in the current working directory.
    // Set the third parameter to '' to load all env regardless of the `VITE_` prefix.
    const env = loadEnv(mode, process.cwd(), '')

    return {
        plugins: [vue()],
        resolve: {
            alias: {
                '@': '/src',
            },
        },
        define: {
            // Expose SERVER_URL to your client-side code
            'import.meta.env.VITE_SERVER_URL': JSON.stringify(env.SERVER_URL)
        }
    }
});
