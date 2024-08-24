<template>
  <!-- Category Selection -->
  <a-form-item :label="$t('select_category', 'Select Category')">
    <a-select
        style="min-width: 100%!important;"
        v-model="selectedCategory"
        :placeholder="$t('select_category_placeholder', 'Select a category')"
        @change="filterModels"
    >
      <a-select-option v-for="category in availableCategories" :key="category" :value="category">
        {{ category }}
      </a-select-option>
    </a-select>
  </a-form-item>

  <!-- Models Selection -->
  <a-form-item :label="$t('select_model', 'Select Models')">
    <a-select
        style="min-width: 100%!important;"
        :value="modelsStore.selectedModels"
        mode="multiple"
        :placeholder="$t('select_model_placeholder', 'Select one or more models')"
        @change="updateModels"
    >


      <!-- OpenAI Models Group -->
      <a-select-opt-group :label="$t('openai_models', 'OpenAI Models')">
        <a-select-option v-for="model in filteredOpenaiModels" :key="model.id" :value="model.id">
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
    const openaiModels = ref([])
    const selectedCategory = ref('')  // To store the selected category
    const filteredOpenaiModels = ref([]) // To store the filtered OpenAI models

    const loadModels = async () => {
      try {
        const data = await getModels()
        localModels.value = data.local_models

        openaiModels.value = data.openai_models.map(model => ({
          id: model.id,
          category: model.category || 'Uncategorized'  // Default to 'Uncategorized' if no category
        }))

        // Ensure selected models are valid
        modelsStore.selectedModels = modelsStore.selectedModels.filter(
            model => localModels.value.includes(model) || openaiModels.value.some(m => m.id === model)
        )

        // Automatically select the first available model if none are selected
        if (modelsStore.selectedModels.length === 0) {
          if (localModels.value.length > 0) {
            modelsStore.setSelectedModels([localModels.value[0]])
          } else if (openaiModels.value.length > 0) {
            modelsStore.setSelectedModels([openaiModels.value[0].id])
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
        filteredOpenaiModels.value = openaiModels.value.filter(model => model.category === category)
      } else {
        filteredOpenaiModels.value = openaiModels.value
      }

      // Update the selected models in the store to ensure only valid models are selected
      modelsStore.selectedModels = modelsStore.selectedModels.filter(
          model => localModels.value.includes(model) || filteredOpenaiModels.value.some(m => m.id === model)
      )
    }

    const updateModels = async (values) => {
      // Update the selected models in the store
      await modelsStore.setSelectedModels(values)
    }

    const availableCategories = computed(() => {
      const categories = openaiModels.value.map(model => model.category)
      return [...new Set(categories)] // Return unique categories
    })

    onMounted(async () => {
      await modelsStore.loadFromStorage()
      await loadModels()
    })

    return {
      modelsStore,
      localModels,
      openaiModels,
      selectedCategory,
      filteredOpenaiModels,
      availableCategories,
      filterModels,
      updateModels,
    }
  },
})
</script>
