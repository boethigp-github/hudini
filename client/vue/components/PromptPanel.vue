<!--suppress CssUnusedSymbol -->
<template>
    <div class="prompt-panel">
        <a-collapse v-model:activeKey="activeKey" accordion>
            <a-collapse-panel v-for="prompt in previousPrompts" :key="prompt.id">
                <template #header>
                    <div class="panel-header">
                        <span class="timestamp">{{ formatTimestamp(prompt.timestamp) }}</span>
                        <div class="header-actions">
                            <icon-copy @click.stop="copyToClipboard(prompt.prompt)" class="copy-icon" />
                            <a-button type="link" @click.stop="deletePrompt(prompt.id)" class="delete-button">
                                {{ $t('delete') }}
                            </a-button>
                        </div>
                    </div>
                    <span class="title">{{ getTitle(prompt) }}</span>
                </template>
                <div class="prompt-content">
                    {{ prompt.prompt }}
                    <icon-copy @click.stop="copyToClipboard(prompt.prompt)" class="copy-icon" />
                    <a-button type="link" @click="deletePrompt(prompt.id)" class="delete-button">
                        {{ $t('delete') }}
                    </a-button>
                </div>
            </a-collapse-panel>
        </a-collapse>
    </div>
</template>

<script>
import { ref, defineComponent, onMounted } from "vue";
import { useI18n } from 'vue-i18n';
import { message, Collapse, Button } from "ant-design-vue";
import { CopyOutlined } from "@ant-design/icons-vue";

export default defineComponent({
    components: {
        IconCopy: CopyOutlined,
        ACollapse: Collapse,
        ACollapsePanel: Collapse.Panel,
        AButton: Button,
    },
    setup() {
        const { t } = useI18n();
        const previousPrompts = ref([]);
        const serverUrl = import.meta.env.VITE_SERVER_URL || "http://localhost:5000";
        const activeKey = ref([]);

        const copyToClipboard = (text) => {
            navigator.clipboard
                .writeText(text)
                .then(() => {
                    message.success(t('copied_to_clipboard'));
                })
                .catch((error) => {
                    message.error(t('failed_to_copy'));
                    console.error("Copy failed:", error);
                });
        };

        const loadPrompts = () => {
            fetch(`${serverUrl}/prompt`)
                .then(res => {
                    if (!res.ok) {
                        throw new Error("Failed to load prompts");
                    }
                    return res.json();
                })
                .then(data => {
                    previousPrompts.value = data;
                })
                .catch(error => {
                    console.error("Error loading prompts:", error);
                    message.error(t('failed_to_prompts'));
                });
        };

        const deletePrompt = (id) => {
            fetch(`${serverUrl}/prompt/${id}`, {
                method: "DELETE",
            })
                .then(res => {
                    if (res.ok) {
                        loadPrompts();  // Reload the prompts after deletion
                        message.success(t('prompt_deleted'));
                    } else {
                        throw new Error("Failed to delete prompt");
                    }
                })
                .catch(error => {
                    console.error("Error deleting prompt", error);
                });
        };

        const getTitle = (prompt) => {
            if (!prompt.prompt) return;
            let title = prompt.prompt.substring(0, 200);
            if (title.length >= 200) {
                title += "...";
            }
            return title;
        };

        const formatTimestamp = (timestamp) => {
            const date = new Date(timestamp);
            const day = String(date.getDate()).padStart(2, "0");
            const month = String(date.getMonth() + 1).padStart(2, "0");
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
            t,
            copyToClipboard,
            previousPrompts,
            activeKey,
            deletePrompt,
            getTitle,
            formatTimestamp,
            loadPrompts, // Return loadPrompts to allow reloading
        };
    }
});
</script>

<style >
.prompt-panel {
    max-height: 70vh; /* Adjust this value to control the panel height */
    overflow-y: auto; /* Ensure the content is scrollable */
    padding-right: 8px; /* Add some padding to avoid cutting off content */
}

.acollapse {
    max-height: 100%; /* Make sure the collapse container fills the parent height */
    overflow-y: auto; /* Ensure content inside the collapse panel is scrollable */
}

.acollapse-panel {
    background: #fff9f9; /* Adjust the background color */
}

.panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.timestamp {
    font-size: 12px;
    color: #666;
}

.header-actions {
    display: flex;
    gap: 10px;
}

.copy-icon {
    cursor: pointer;
    font-size: 16px;
    color: #999;
}

.delete-button {
    color: red;
    font-size: 12px;
}

.prompt-content {
    padding-top: 10px;
    padding-bottom: 10px;
}

/* Previous Prompts */
.previous-prompts {
    background-color: #fff;
    padding: 20px;
    border-radius: 10px;
    width:100%;
    max-width:100%!important;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    height: 83vh;
    align-items: center; /* Optional: Center vertically */
}

</style>
