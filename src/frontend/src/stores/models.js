import { defineStore } from 'pinia'
import localforage from 'localforage'

// Initialize localforage
localforage.config({
    name: 'MyApp',
    storeName: 'models' // This is the name of our IndexedDB database
})

export const useModelsStore = defineStore('models', {
    state: () => ({
        selectedModels: []
    }),
    actions: {
        async setSelectedModels(models) {
            this.selectedModels = models;
            await this.saveToStorage();
        },
        async loadFromStorage() {
            const storedModels = await localforage.getItem('models');
            if (storedModels) {
                try {
                    this.selectedModels = JSON.parse(storedModels);
                } catch (error) {
                    console.error("Failed to parse stored models:", error);
                }
            }
        },
        async saveToStorage() {
            try {
                await localforage.setItem('models', JSON.stringify(this.selectedModels));
            } catch (error) {
                console.error("Failed to save models to storage:", error);
            }
        }
    },
    persist: true // We'll handle persistence manually
});
