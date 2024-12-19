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
        :item-height="50"
      >
        <template v-slot:default="{ item }">
          <v-expansion-panel :key="item.id">
            <template v-slot:title>
              <div class="panel-content">
                <div class="panel-header">
                  <span class="title">{{ item.title }}</span>
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
import { ref, onMounted, computed, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { fetchPrompts, deletePromptById } from "@/vue/services/api.js";
import debounce from 'lodash/debounce';

const { t } = useI18n();
const previousPrompts = ref([]);
const searchQuery = ref('');
const activeKey = ref([]);
const serverUrl = import.meta.env.SERVER_URL;

if (!serverUrl) {
  console.error("SERVER_URL not set. Check Env. All envs", import.meta.env);
}

// Debounced search query to optimize reactivity
const debouncedQuery = ref('');
const updateSearch = debounce((value) => {
  debouncedQuery.value = value;
}, 300);

watch(searchQuery, (value) => {
  updateSearch(value);
});

// Filtered prompts based on search query
const filteredPrompts = computed(() => {
  if (!debouncedQuery.value) return previousPrompts.value;
  return previousPrompts.value.filter(prompt =>
    prompt.title.toLowerCase().includes(debouncedQuery.value.toLowerCase())
  );
});

const loadPrompts = async () => {
  try {
    const response = await fetchPrompts();
    previousPrompts.value = response.map(prompt => ({
      ...prompt,
      title: prompt.prompt ? prompt.prompt.substring(0, 200) + (prompt.prompt.length > 200 ? "..." : "") : "",
    }));
  } catch (error) {
    console.error('Failed to load prompts:', error);
  }
};

const deletePrompt = async (id) => {
  try {
    await deletePromptById(id);
    await loadPrompts();
  } catch (error) {
    console.error('Failed to delete prompt:', error);
  }
};

const rerunPrompt = (prompt) => {
  const event = new CustomEvent('rerun-prompt', {
    detail: prompt,
  });
  window.dispatchEvent(event);
};

const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text);
    console.log(t('copied_to_clipboard'));
  } catch (error) {
    console.error(t('failed_to_copy'));
    console.error("Copy failed:", error);
  }
};

const formatTimestamp = (timestamp) => {
  const date = new Date(timestamp);
  return date.toLocaleString('de-DE', { dateStyle: 'short', timeStyle: 'medium' });
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