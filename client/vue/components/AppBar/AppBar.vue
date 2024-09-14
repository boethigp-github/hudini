<template>
  <v-app-bar class="v-app-bar" name="app-bar" density="compact" :elevation="10">
    <v-container fluid>
      <v-row align="center" no-gutters>
        <v-col cols="auto">
          <img
            src="/assets/hudini.webp"
            height="40"
            width="40"
            class="mr-2"
          ></img>
        </v-col>
        <v-app-bar-title>Hudini, bra... </v-app-bar-title>
        <v-spacer></v-spacer>
        <v-col class="theme-switch-container" cols="auto">
          <ThemeSwitch/>
        </v-col>
        <v-spacer></v-spacer>
        <v-col class="theme-switch-container" cols="auto">
          <FileManager/>
        </v-col>
        <v-spacer></v-spacer>
        <v-col class="language-switch-container" cols="auto">
          <LanguageSwitch/>
        </v-col>
      </v-row>
    </v-container>
  </v-app-bar>
</template>

<script setup>
import ThemeSwitch from "@/vue/components/ThemeSwitch.vue";
import LanguageSwitch from "@/vue/components/LanguageSwitch.vue";
import FileManager from "@/vue/components/ContextManager/ContextManager.vue";
</script>

<style scoped>
.v-app-bar-title {
  margin-left: 8px;
}
</style>