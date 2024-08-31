<!--suppress CssUnusedSymbol -->
<template>
       <a-card size="small" class="previous-prompt-card" :title="$t('previous_prompts')" >
  <div class="prompt-panel">
        <a-collapse v-model:activeKey="activeKey" accordion>
            <a-collapse-panel v-for="prompt in previousPrompts" :key="prompt.id">
                <template #header>
                    <div class="panel-header">
                        <span class="timestamp">{{ formatTimestamp(prompt.timestamp) }}</span>
                        <div class="header-actions">
                            <icon-copy @click.stop="copyToClipboard(prompt.prompt)" class="copy-icon" :title=" $t('copy_clipboard', 'Copy to clipboard')" />
                            <icon-delete @click.stop="deletePrompt(prompt.id)" class="copy-icon" :title=" $t('delete')" />
                        </div>
                    </div>
                    <span class="title">{{ getTitle(prompt) }}</span>
                </template>
                <div class="prompt-content">
                    {{ prompt.prompt }}
                </div>
            </a-collapse-panel>
        </a-collapse>
    </div>
       </a-card>
</template>

<script>
import { ref, defineComponent, onMounted } from "vue";
import { useI18n } from 'vue-i18n';
import { message, Collapse, Button } from "ant-design-vue";
import { CopyOutlined, DeleteFilled } from "@ant-design/icons-vue";
import { Card } from 'ant-design-vue';
export default defineComponent({
    components: {
        IconCopy: CopyOutlined,
        IconDelete: DeleteFilled,
        ACollapse: Collapse,
        ACollapsePanel: Collapse.Panel,
        AButton: Button,
      'a-card': Card,
    },
    setup() {
        const { t } = useI18n();
        const previousPrompts = ref([]);
        const serverUrl = import.meta.env.SERVER_URL;

      if (!serverUrl) {
        console.error("SERVER_URL not set. Check Env. All envs", import.meta.env);
      }
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
    max-height: 66.5vh;
    overflow-y: auto;
    width: 100%;
}


.previous-prompt-card{
  width: 100%!important;

  margin-top: 0;

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

.copy-icon, .copy-icon {
    cursor: pointer;
    font-size: 16px;
    color: #999;
    margin-right: -5px;
    margin-top: -13px;
}

.copy-icon:hover{
  color: #999;
}

.delete-button {
    color: red;
    font-size: 12px;
    margin-top: -20px;
  margin-right: -20px;
}

.prompt-content {
    padding-top: 10px;
    padding-bottom: 10px;
}

/* Previous Prompts */
.previous-prompts {
    background:none;
    padding: 0;
    border-radius: 10px;
    width:40%;
    max-width:100%!important;
    height: 89vh;
    align-items: center; /* Optional: Center vertically */
}

</style>
