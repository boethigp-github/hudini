<template>
  <div class="selected-models-list">
    <v-list style="margin: 0;padding: 0" v-if="hasSelectedModels">
      <template v-for="(models, category) in groupedSelectedModels" :key="category">
        <v-list-item class="selected-models-item" density="compact" v-for="model in models" :key="model.id">
          <v-list-item-title>- {{ model.id }}</v-list-item-title>
        </v-list-item>
      </template>
    </v-list>
    <v-progress-circular v-else-if="loading" indeterminate></v-progress-circular>
    <div v-else type="info">{{ $t('no_models_selected', 'No models selected') }}</div>
  </div>
</template>

<script>
import { defineComponent, ref, computed, onMounted, watch } from 'vue';
import { useModelsStore } from '../../stores/models.js';
import { loadModels, filterModels, getAvailableCategories } from '../../services/models.js';

export default defineComponent({
  name: 'SelectedModelsList',
  setup() {
    const modelsStore = useModelsStore();
    const allModels = ref([]);
    const selectedModels = ref([]);
    const loading = ref(true);

    const fetchModels = async () => {
      loading.value = true;
      try {



        allModels.value = await loadModels();
        updateSelectedModels();
      } catch (error) {
        console.error("Failed to fetch models:", error);
        allModels.value = [];
      }
      loading.value = false;
    };

    const updateSelectedModels = () => {
      selectedModels.value = allModels.value.filter(model =>
          modelsStore.selectedModels.includes(model.id)
      );
    };

    const hasSelectedModels = computed(() => selectedModels.value.length > 0);

    const groupedSelectedModels = computed(() => {
      const grouped = {};
      selectedModels.value.forEach(model => {
        const category = model.category || 'Uncategorized';
        if (!grouped[category]) {
          grouped[category] = [];
        }
        grouped[category].push(model);
      });
      return grouped;
    });

    onMounted(fetchModels);

    watch(() => modelsStore.selectedModels, updateSelectedModels);

    return {
      groupedSelectedModels,
      hasSelectedModels,
      loading
    };
  }
});
</script>

<style scoped>
.selected-models-list {
  max-height: 200px;
  overflow-y: auto;
}

.v-list-item-title {
  font-size: 11px;
  margin: 5px;
}
</style>