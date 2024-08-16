<template>
    <h2>{{ $t('previous_prompts') }}</h2>
    <a-collapse  :style="{background:'#fff9f9', marginBottom:'10px'}" v-model:activeKey="activeKey" accordion>
        <a-collapse-panel v-for="prompt in previousPrompts" :key="prompt.id" :style="{background:'#fff9f9'}">
            <template #header>
                <div class="panel-header">
                    <span class="timestamp">{{ formatTimestamp(prompt.timestamp) }}</span>
                    <div class="header-actions">
                        <icon-copy
                            @click.stop="copyToClipboard(prompt.prompt)"
                            class="copy-icon"
                        />
                        <a-button
                            type="link"
                            @click.stop="deletePrompt(prompt.id)"
                            class="delete-button"
                        >
                            {{ $t('delete') }}
                        </a-button>
                    </div>
                </div>
                <span class="title">{{ getTitle(prompt) }}</span>

            </template>
            <div class="prompt-content">
                {{ prompt.prompt }}
                <icon-copy
                    @click.stop="copyToClipboard(prompt.prompt)"
                    class="copy-icon"
                />
                <a-button
                    type="link"
                    @click="deletePrompt(prompt.id)"
                    class="delete-button"
                >
                    {{ $t('delete') }}
                </a-button>
            </div>
        </a-collapse-panel>
    </a-collapse>
</template>

<script>
import { ref, defineComponent, onMounted } from "vue";
import { useI18n } from 'vue-i18n';
import { message, Collapse, Button } from "ant-design-vue"; // Import necessary components
import { CopyOutlined } from "@ant-design/icons-vue"; // For the copy icon

export default defineComponent({
    components: {
        IconCopy: CopyOutlined,
        ACollapse: Collapse,
        ACollapsePanel: Collapse.Panel,
        AButton: Button,
    },
    setup() {
        const { t } = useI18n();  // Accessing the translation function

        const previousPrompts = ref([]);
        const serverUrl =
            import.meta.env.VITE_SERVER_URL || "http://localhost:5000";
        const activeKey = ref([]); // Initialize as an empty array for accordion behavior

        const copyToClipboard = (text) => {
            navigator.clipboard
                .writeText(text)
                .then(() => {
                    message.success(t('copied_to_clipboard'));  // Use translation
                })
                .catch((error) => {
                    message.error(t('failed_to_copy'));  // Use translation
                    console.error("Copy failed:", error);
                });
        };

        const loadPrompts = async () => {
            try {
                const res = await fetch(`${serverUrl}/load_prompts`);
                if (!res.ok) { // noinspection ExceptionCaughtLocallyJS
                    throw new Error("Failed to load prompts");
                }
                previousPrompts.value = await res.json();
            } catch (error) {
                console.error("Error loading prompts:", error);
            }
        };



        const deletePrompt = async (id) => {
            try {
                const res = await fetch(`${serverUrl}/delete_prompt/${id}`, {
                    method: "DELETE",
                });

                if (res.ok) {
                    await loadPrompts();
                    message.success(t('prompt_deleted'));  // Use translation
                }
            } catch (error) {
                console.error("Error deleting prompt", error);
            }
        };

        const getTitle = (prompt) => {

            if (!prompt.prompt) {
                return;
            }
            let title = prompt.prompt.substring(0, 200);

            if (title.length >= 200) {
                title += "...";
            }
            return title; // Get the first 200 characters
        };

        const formatTimestamp = (timestamp) => {
            const date = new Date(timestamp);
            const day = String(date.getDate()).padStart(2, "0");
            const month = String(date.getMonth() + 1).padStart(2, "0"); // Months are zero-based
            const year = date.getFullYear();
            const hours = String(date.getHours()).padStart(2, "0");
            const minutes = String(date.getMinutes()).padStart(2, "0");
            const seconds = String(date.getSeconds()).padStart(2, "0");

            return `${day}.${month}.${year} ${hours}:${minutes}:${seconds}`;
        };

        onMounted(() => {
            loadPrompts(); // Load prompts when the component is mounted
        });

        return {
            t,  // Make the translation function available in the template
            copyToClipboard,
            previousPrompts,
            activeKey,
            deletePrompt,
            getTitle,
            formatTimestamp,
        };
    },
});
</script>
