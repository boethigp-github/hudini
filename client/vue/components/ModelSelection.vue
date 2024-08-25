<template>
  <!-- Category Selection -->
  <a-form-item :label="$t('select_category_and_model', 'Select Category / Model') "  style="min-width:100%;max-width: 30%!important;float:left">
    <a-select
        style="min-width: 30%!important;float:left; margin-right: 5px"
        v-model="selectedCategory"
        :placeholder="$t('select_category_placeholder', 'Select a category')"
        @change="filterModels"
    >
      <a-select-option v-for="category in availableCategories" :key="category" :value="category">
        {{ category }}
      </a-select-option>

    </a-select>
    <a-select
        style="min-width: 65%!important;float:right "
        :value="modelsStore.selectedModels"
        mode="multiple"
        :placeholder="$t('select_model_placeholder', 'Select one or more models')"
        @change="updateModels"
    >
      <!-- OpenAI Models Group -->
      <a-select-opt-group :label="$t('models', 'Models')">
        <a-select-option v-for="model in filteredModels" :key="model.id" :value="model.id">
          {{ model.id }} ({{ model.category }})
        </a-select-option>
      </a-select-opt-group>
    </a-select>
  </a-form-item>

</template>

<script>
import { defineComponent, ref, onMounted, computed } from 'vue'
import { useModelsStore } from './../stores'
import { getModels } from './../services/api'

export default defineComponent({
  name: 'ModelSelection',
  setup() {
    const modelsStore = useModelsStore()
    const localModels = ref([])
    const models = ref([])
    const selectedCategory = ref('')  // To store the selected category
    const filteredModels = ref([]) // To store the filtered OpenAI models

    const loadModels = async () => {
      try {
        const data = await getModels()
    

        models.value = data.map(model => ({
          id: model.id,
          category: model.category || 'Uncategorized',  // Default to 'Uncategorized' if no category
          platform: model.platform || 'Uncategorized',  // Default to 'Uncategorized' if no category
        }))

        // Ensure selected models are valid
        modelsStore.selectedModels = modelsStore.selectedModels.filter(
            model => localModels.value.includes(model) || models.value.some(m => m.id === model)
        )

        // Automatically select the first available model if none are selected
        if (modelsStore.selectedModels.length === 0) {
          if (models.value.length > 0) {
            modelsStore.setSelectedModels([models.value[0].id])
          }
        }

        // Initial filtering based on the default or stored selected category
        filterModels(selectedCategory.value)
      } catch (error) {
        console.error('Failed to load models:', error)
      }
    }

    // Filter models based on the selected category
    const filterModels = (category) => {
      if (category) {
        filteredModels.value = models.value.filter(model => model.category === category)
      } else {
        filteredModels.value = models.value
      }

      // Update the selected models in the store to ensure only valid models are selected
      modelsStore.selectedModels = modelsStore.selectedModels.filter(
          model => localModels.value.includes(model) || filteredModels.value.some(m => m.id === model)
      )
    }

    const updateModels = async (values) => {
      // Update the selected models in the store
      await modelsStore.setSelectedModels(values)
    }

    const availableCategories = computed(() => {
      const categories = models.value.map(model => model.category)
      return [...new Set(categories)] // Return unique categories
    })

    onMounted(async () => {
      await modelsStore.loadFromStorage()
      await loadModels()
    })

    return {
      modelsStore,
      localModels,
      models: models,
      selectedCategory,
      filteredModels,
      availableCategories,
      filterModels,
      updateModels,
    }
  },
})
</script>
