<template>
  <v-combobox
    class="select-category"
    v-model="selectedCategory"
    :items="availableCategories"
    :label="$t('select_category_placeholder', 'Select a category')"
    clearable
    @update:modelValue="onCategoryChange"
  ></v-combobox>
  <v-combobox
    v-model="modelsStore.selectedModels"
    :items="filteredModels.map(item => item.id)"
    :label="$t('select_model_placeholder', 'Select one or more models')"
    chips
    multiple
    clearable
    @update:modelValue="onModelsChange"
  ></v-combobox>
</template>

<script>
import { defineComponent, ref, onMounted, computed } from 'vue';
import { useModelsStore } from '../../stores/index.js';
import { loadModels, filterModels, updateModels, getAvailableCategories } from '../../services/models.js';

export default defineComponent({
  name: 'ModelSelection',
  setup() {
    const modelsStore = useModelsStore();
    const models = ref([]);
    const filteredModels = ref([]);
    const selectedCategory = ref('');

    const loadAndFilterModels = async () => {
      await modelsStore.loadFromStorage();
      models.value = await loadModels();
      onCategoryChange(selectedCategory.value);
    };

    const onCategoryChange = (category) => {
      filteredModels.value = filterModels(models.value, category);
    };

    const onModelsChange = async (values) => {
      await updateModels(values);
    };

    const availableCategories = computed(() => getAvailableCategories(models.value));

    onMounted(loadAndFilterModels);

    return {
      modelsStore,
      selectedCategory,
      filteredModels,
      availableCategories,
      onCategoryChange,
      onModelsChange,
    };
  },
});
</script>

<style scoped>
.select-category {
  margin-right: 5px;
  min-width: 50%;
}
</style>