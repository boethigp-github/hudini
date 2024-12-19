import { getModels } from './api.js';
import { useModelsStore } from '../stores/index.js';

export async function loadModels() {
  const modelsStore = useModelsStore();
  try {
    const data = await getModels();


    // Save the complete service response
    await modelsStore.saveServiceResponse(data);

    if(!data?.length) return [];

    const models = data.map(model => ({
      id: model.id,
      category: model.category || 'Uncategorized',
      platform: model.platform || 'Uncategorized',
    }));


    // Ensure selected models are valid
    modelsStore.selectedModels = modelsStore.selectedModels.filter(
      model => models.some(m => m.id === model)
    );


    // Automatically select the first available model if none are selected
    if (modelsStore.selectedModels.length === 0 && models.length > 0) {
      await modelsStore.setSelectedModels([models[0].id]);
    }

    return models;
  } catch (error) {
    console.error('Failed to load models:', error);
    return [];
  }
}

export function filterModels(models, category) {
  const modelsStore = useModelsStore();
  let filteredModels;
  if (category) {
    filteredModels = models.filter(model => model.category === category);
  } else {
    filteredModels = models;
  }

  // Update the selected models in the store to ensure only valid models are selected
  modelsStore.selectedModels = modelsStore.selectedModels.filter(
    model => filteredModels.some(m => m.id === model)
  );

  return filteredModels;
}

export async function updateModels(values) {
  const modelsStore = useModelsStore();
  // Update the selected models in the store
  await modelsStore.setSelectedModels(values);
}

export function getAvailableCategories(models) {
  const categories = models.map(model => model.category);
  return [...new Set(categories)]; // Return unique categories
}