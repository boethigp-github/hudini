import { defineStore } from 'pinia';
import localforage from 'localforage';

// Initialize localforage
localforage.config({
  name: 'Hudini',
  storeName: 'auth' // This is the name of our IndexedDB database for authentication info
});

export const useAuthStore = defineStore('auth', {
  actions: {
    async setUser(user) {
      await localforage.setItem('user', JSON.stringify(user));
    },

    async removeUser() {
      await localforage.removeItem('user');
    },

    async loadFromStorage() {
      const storedUser = await localforage.getItem('user');
      return storedUser ? JSON.parse(storedUser) : null;
    }
  }
});
