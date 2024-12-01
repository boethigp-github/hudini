<template>
  <v-dialog
      v-model="isModelSelectionViewVisible"
      min-width="500px"
      width="50%"
      :retain-focus="false"
  >
    <v-card min-width="50%">
      <v-card-title class="text-h5 pa-4">
         {{$t('model_selection', 'Select Models')}}
        <v-btn
            icon="mdi-close"
            variant="text"
            @click="closeDialog"
            class="float-right"
        ></v-btn>
      </v-card-title>

      <v-card-text class="pa-4">
       <ModelSelection/>
      </v-card-text>

      <v-card-actions class="pa-4">
        <v-spacer></v-spacer>
        <v-btn color="primary" @click="closeDialog">OK</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import {onBeforeUnmount, onMounted, ref} from 'vue'
import ModelSelection from "@/vue/components/ModelSelection/ModelSelection.vue";

export default {
  components: {ModelSelection},
  setup() {


    const isModelSelectionViewVisible = ref(false);

    const closeDialog = () => {
      isModelSelectionViewVisible.value = false
    }

    onMounted(async () => {
      window.addEventListener('open-model-selection', onOpenModelSelection);
    });

    onBeforeUnmount(() => {
      window.removeEventListener('open-model-selection', onOpenModelSelection);
    });

    const onOpenModelSelection = async (event) => {
      isModelSelectionViewVisible.value = !isModelSelectionViewVisible.value;
    };


    return {
      isModelSelectionViewVisible,
      closeDialog
    }
  }
}
</script>

<style scoped>
.float-right {
  position: absolute;
  top: 8px;
  right: 8px;
}
</style>