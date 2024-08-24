<template>
    <a-form-item :label="$t('select_model', 'Select Models')">
        <a-select
            :value="modelsStore.selectedModels"
            mode="multiple"
            :placeholder="$t('select_model_placeholder', 'Select one or more models')"
            @change="updateModels"
        >
            <a-select-opt-group :label="$t('local_models', 'Local Models')">
                <a-select-option v-for="model in localModels" :key="model" :value="model">
                    {{ model }}
                </a-select-option>
            </a-select-opt-group>
            <a-select-opt-group :label="$t('openai_models', 'OpenAI Models')">
                <a-select-option v-for="model in openaiModels" :key="model" :value="model">
                    {{ model }}
                </a-select-option>
            </a-select-opt-group>
        </a-select>
    </a-form-item>
</template>

<script>
import { defineComponent, ref, onMounted } from 'vue'
import { useModelsStore } from './../stores'
import { getModels } from './../services/api'

export default defineComponent({
    name: 'ModelSelection',
    setup() {
        const modelsStore = useModelsStore()
        const localModels = ref([])
        const openaiModels = ref([])

        const loadModels = async () => {
            try {
                const data = await getModels()
                localModels.value = data.local_models
                openaiModels.value = data.openai_models

                // This ensures that selected models are validated against the available models
                modelsStore.selectedModels = modelsStore.selectedModels.filter(
                    model => localModels.value.includes(model) || openaiModels.value.includes(model)
                )

                // If no models are selected after filtering, select the first available one
                if (modelsStore.selectedModels.length === 0) {
                    if (localModels.value.length > 0) {
                        modelsStore.setSelectedModels([localModels.value[0]])
                    } else if (openaiModels.value.length > 0) {
                        modelsStore.setSelectedModels([openaiModels.value[0]])
                    }
                }
            } catch (error) {
                console.error('Failed to load models:', error)
            }
        }

        const updateModels = async (values) => {
            await modelsStore.setSelectedModels(values)
        }

        onMounted(async () => {
            await modelsStore.loadFromStorage()
            await loadModels()
        })

        return {
            modelsStore,
            localModels,
            openaiModels,
            updateModels,
        }
    },
})
</script>
