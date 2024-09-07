<template>
  <a-card size="small" class="previous-prompt-card" :title="$t('previous_prompts')">
    <div class="prompt-panel">
      <a-collapse v-model:activeKey="activeKey" accordion>
        <a-collapse-panel v-for="prompt in previousPrompts" :key="prompt.id">
          <template #header>
            <div class="panel-header">
              <span class="timestamp">{{ formatTimestamp(prompt.created_at) }}</span>
              <div class="header-actions">
                <!-- Rerun icon added here -->
                <a-popover trigger="hover" placement="bottomLeft">
                  <template #content>
                    <p>{{ $t('rerun_prompt', 'Rerun Prompt') }}</p>
                  </template>
                  <icon-rerun @click.stop="rerunPrompt(prompt)" class="rerun-icon"
                              :title="$t('rerun_prompt', 'Rerun Prompt')"/>
                </a-popover>
                <a-popover trigger="hover"  placement="bottomLeft">
                  <template #content>
                    <p>{{ $t('copy_clipboard', 'Copy to clipboard') }}</p>
                  </template>
                  <icon-copy @click.stop="copyToClipboard(prompt.prompt)" class="copy-icon"
                             :title="$t('copy_clipboard', 'Copy to clipboard')"/>
                </a-popover>
                <a-popover trigger="hover"  placement="bottomLeft">
                  <template #content>
                    <p>{{ $t('delete') }}</p>
                  </template>
                  <icon-delete @click.stop="deletePrompt(prompt.uuid)" class="delete-icon" :title="$t('delete')"/>
                </a-popover>
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
import {ref, defineComponent, onMounted} from "vue";
import {useI18n} from 'vue-i18n';
import {message, Collapse, Button} from "ant-design-vue";
import {CopyOutlined, DeleteFilled, RedoOutlined} from "@ant-design/icons-vue";
import {Card} from 'ant-design-vue';

export default defineComponent({
  components: {
    IconCopy: CopyOutlined,
    IconDelete: DeleteFilled,
    IconRerun: RedoOutlined, // New Rerun Icon
    ACollapse: Collapse,
    ACollapsePanel: Collapse.Panel,
    AButton: Button,
    'a-card': Card,
  },
  setup() {
    const {t} = useI18n();
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
      fetch(`${serverUrl}/prompts`)
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
      fetch(`${serverUrl}/prompts/${id}`, {
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

    const rerunPrompt = (prompt) => {
      const event = new CustomEvent('rerun-prompt', {
        detail: prompt,
      });
      window.dispatchEvent(event);
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
      rerunPrompt, // Expose rerunPrompt function
      getTitle,
      formatTimestamp,
      loadPrompts, // Return loadPrompts to allow reloading
    };
  }
});
</script>

<style scoped>
.prompt-panel {
  height: auto;
  max-height: 66.5vh;
  min-height: 66.5vh;
  overflow-y: auto;
  width: 100%;
}

.previous-prompt-card {
  width: 100% !important;
  margin-top: 0;
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

.copy-icon, .rerun-icon, .delete-icon {
  cursor: pointer;
  font-size: 16px;
  color: #999;
  margin-right: -5px;
  margin-top: -13px;
}

.delete-icon {
  color: orange;
}

.rerun-icon {
  color: darkolivegreen;
}

.copy-icon:hover, .rerun-icon:hover, .delete-icon:hover {
  color: #0e4980 !important;
}


.rerun-icon:hover, .copy-icon:hover, .delete-icon:hover {
  color: #999;
}


.prompt-content {
  padding-top: 10px;
  padding-bottom: 10px;
}

/* Previous Prompts */
.previous-prompts {
  background: none;
  padding: 0;
  border-radius: 10px;
  width: 40%;
  max-width: 100% !important;
  height: 89vh;
  align-items: center; /* Optional: Center vertically */
}
</style>