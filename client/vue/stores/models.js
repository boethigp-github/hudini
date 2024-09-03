import {defineStore} from 'pinia'
import localforage from 'localforage'

// Initialize localforage
localforage.config({
    name: 'MyApp',
    storeName: 'models' // This is the name of our IndexedDB database
})

export const useModelsStore = defineStore('models', {
    state: () => ({
        selectedModels: [],
        serviceResponse: null
    }),
    actions: {
        async setSelectedModels(models) {
            this.selectedModels = models;
            await this.saveToStorage();
        },

        async getSelectedModelsWithMetaData() {
               return this.selectedModels.map((modelId) => {
                const fullModelInfo = this.serviceResponse.find((model) => model.id === modelId);
                return fullModelInfo || {id: modelId, platform: 'unknown'};
            });
        },

        async loadFromStorage() {
            const storedModels = await localforage.getItem('selectedModels');
            if (storedModels) {
                try {
                    this.selectedModels = JSON.parse(storedModels);
                } catch (error) {
                    console.error("Failed to parse stored models:", error);
                }
            }

            const storedResponse = await localforage.getItem('serviceResponse');
            if (storedResponse) {
                try {
                    this.serviceResponse = JSON.parse(storedResponse);
                } catch (error) {
                    console.error("Failed to parse stored service response:", error);
                }
            }
        },
        async saveToStorage() {
            try {
                await localforage.setItem('selectedModels', JSON.stringify(this.selectedModels));
                await localforage.setItem('serviceResponse', JSON.stringify(this.serviceResponse));
            } catch (error) {
                console.error("Failed to save to storage:", error);
            }
        },
        async saveServiceResponse(response) {
            this.serviceResponse = response;
            await this.saveToStorage();
        },
        async getServiceResponse() {
            if (this.serviceResponse) {
                return this.serviceResponse;
            }

            const storedResponse = await localforage.getItem('serviceResponse');
            if (storedResponse) {
                try {
                    this.serviceResponse = JSON.parse(storedResponse);
                    return this.serviceResponse;
                } catch (error) {
                    console.error("Failed to parse stored service response:", error);
                }
            }

            return null; // Return null if no service response is found
        }
    },
    persist: true // We'll handle persistence manually
});


