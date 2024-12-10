<template>
  <div>
    <v-btn
      class="contextmanager-opener"
      icon="mdi-head-snowflake"
      color="primary"
      size="small"
      elevation="2"
      :title="t('open_context_manager', 'Hudinis Brain')"
      @click="isModalOpen = true"
    ></v-btn>

    <v-dialog height="95%" v-model="isModalOpen" style="min-height: 90vh">
      <v-card  style="min-height: 90vh">
        <v-card-title>{{ t('context_manager', 'Context Manager') }}</v-card-title>
        <v-tabs v-model="activeTab" bg-color="primary">
          <v-tab value="gripsbox">{{ t('hudinis_gripsbox', 'GripsBox') }}</v-tab>
          <v-tab value="model_parameters">{{ t('model_parameters', 'Model Parameters') }}</v-tab>
        </v-tabs>

        <v-card-text>
          <v-tabs-window v-model="activeTab">
            <!-- GripsBox Tab Content -->
            <v-tabs-window-item value="gripsbox">
              <GripsBox />
            </v-tabs-window-item>

            <!-- Model Parameters Tab Content -->
            <v-tabs-window-item value="model_parameters">
                <ModelParameters></ModelParameters>
            </v-tabs-window-item>
          </v-tabs-window>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
import GripsBox from "@/vue/components/Gripsbox/GripsBox.vue";
import ModelParameters from "@/vue/components/Gripsbox/ModelParameters.vue";

const { t } = useI18n();
const isModalOpen = ref(false);
const activeTab = ref('gripsbox'); // Default tab
</script>

<style scoped>
.contextmanager-opener {
  margin-top: -25px;
}
</style>
