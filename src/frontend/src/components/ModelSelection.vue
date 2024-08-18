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
import { defineComponent, onMounted } from 'vue'
import { useModelsStore } from './../stores'

export default defineComponent({
    name: 'ModelSelection',
    props: {
        localModels: {
            type: Array,
            required: true,
        },
        openaiModels: {
            type: Array,
            required: true,
        },
    },
    setup() {
        const modelsStore = useModelsStore()

        const updateModels = async (values) => {
            await modelsStore.setSelectedModels(values)
        }

        onMounted(async () => {
            await modelsStore.loadFromStorage()
        })

        return {
            modelsStore,
            updateModels,
        }
    },
})
</script>
