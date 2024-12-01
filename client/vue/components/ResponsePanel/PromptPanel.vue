<template>
  <v-card class="previous-prompt-card" dense>
    <v-card-title class="text-primary">
      {{ $t('previous_prompts') }} ({{ filteredPrompts.length }})
    </v-card-title>
    <v-card-text>
      <v-text-field
        v-model="searchQuery"
        :label="$t('search_prompts')"
        prepend-inner-icon="mdi-magnify"
        variant="outlined"
        density="compact"
        hide-details
        class="mb-4"
      ></v-text-field>
    </v-card-text>
    <v-expansion-panels variant="accordion" v-model="activeKey">
      <v-virtual-scroll
        class="prompt-panel"
        height="50vh"
        :items="filteredPrompts"
      >
        <template v-slot:default="{ item }">
          <v-expansion-panel :key="item.id">
            <template v-slot:title>
              <div class="panel-content">
                <div class="panel-header">
                  <span class="title">{{ getTitle(item) }}</span>
                  <span class="timestamp" v-if="item.created_at">{{ formatTimestamp(item.created_at) }}</span>
                </div>
                <div class="header-actions">
                  <v-tooltip location="bottom">
                    <template v-slot:activator="{ props }">
                      <v-btn icon="mdi-refresh" size="x-small" v-bind="props" @click.stop="rerunPrompt(item)">
                        <v-icon>mdi-refresh</v-icon>
                      </v-btn>
                    </template>
                    <span>{{ $t('rerun_prompt', 'Rerun Prompt') }}</span>
                  </v-tooltip>
                  <v-tooltip location="bottom">
                    <template v-slot:activator="{ props }">
                      <v-btn icon="mdi-content-copy" size="x-small" v-bind="props" @click.stop="copyToClipboard(item.prompt)">
                        <v-icon>mdi-content-copy</v-icon>
                      </v-btn>
                    </template>
                    <span>{{ $t('copy_clipboard', 'Copy to clipboard') }}</span>
                  </v-tooltip>
                  <v-tooltip location="bottom">
                    <template v-slot:activator="{ props }">
                      <v-btn icon="mdi-delete" size="x-small" v-bind="props" @click.stop="deletePrompt(item.uuid)">
                        <v-icon>mdi-delete</v-icon>
                      </v-btn>
                    </template>
                    <span>{{ $t('delete') }}</span>
                  </v-tooltip>
                </div>
              </div>
            </template>
            <v-expansion-panel-text>
              {{ item.prompt }}
            </v-expansion-panel-text>
          </v-expansion-panel>
        </template>
      </v-virtual-scroll>
    </v-expansion-panels>
  </v-card>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import {fetchPrompts, deletePromptById} from "@/vue/services/api.js";

const { t } = useI18n();
const previousPrompts = ref([]);
const serverUrl = import.meta.env.SERVER_URL;
const searchQuery = ref('');

if (!serverUrl) {
  console.error("SERVER_URL not set. Check Env. All envs", import.meta.env);
}

const activeKey = ref([]);

const filteredPrompts = computed(() => {
  if (!searchQuery.value) return previousPrompts.value;
  return previousPrompts.value.filter(prompt =>
    getTitle(prompt).toLowerCase().includes(searchQuery.value.toLowerCase())
  );
});

const copyToClipboard = (text) => {
  navigator.clipboard
    .writeText(text)
    .then(() => {
      // Replace with Vuetify snackbar or notification system
      console.log(t('copied_to_clipboard'));
    })
    .catch((error) => {
      // Replace with Vuetify snackbar or notification system
      console.error(t('failed_to_copy'));
      console.error("Copy failed:", error);
    });
};

const loadPrompts = () => {
   fetchPrompts().then(response => {
     previousPrompts.value = response;
   })
};

const deletePrompt = async (id) => {
    await deletePromptById(id)
    loadPrompts()
};

const rerunPrompt = (prompt) => {
  const event = new CustomEvent('rerun-prompt', {
    detail: prompt,
  });
  window.dispatchEvent(event);
};

const getTitle = (prompt) => {
  if (!prompt.prompt) return '';
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
</script>

<style scoped>
.prompt-panel {
  height: auto;
  max-height: 50vh;
  min-height: 50vh;
  overflow-y: auto;
  width: 100%;
}

.panel-content {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.timestamp {
  font-size: 12px;
  color: #666;
}

.header-actions {
  gap: 5px;
  margin-top: 8px;
  display: none;
  transition: opacity 0.3s ease;
}

.title {
  font-weight: bold;
  flex-grow: 1;
  color: #858585;
  font-weight: normal;
}

/* Show buttons on hover */
.v-expansion-panel-title:hover .header-actions {
  display: flex;
}
</style>