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

    <v-dialog height="95%" v-model="isModalOpen">
      <v-card>
        <v-card-title> {{ t('hudinis_gripsbox', 'Hudinis Gripsbox') }} </v-card-title>
        <v-card-text>
          <v-file-input
            v-model="files"
            counter
            multiple
            show-size
            :label="t('upload_files', 'Upload Files')"
            @change="handleFileUpload"
          ></v-file-input>
          <v-list>
            <v-list-item v-for="(file, index) in uploadedFiles" :key="index">
              <v-row align="center" no-gutters>
                <v-col cols="12" sm="3" md="2">
                  <v-list-item-title class="text-truncate">
                    <v-icon start icon="mdi-file" size="small"></v-icon>
                    {{ file.name }}
                  </v-list-item-title>
                  <v-list-item-subtitle class="text-truncate">{{ file.size }} bytes</v-list-item-subtitle>
                </v-col>
                <v-col cols="12" sm="2" md="4">
                  <v-combobox
                    v-model="file.tags"
                    :items="availableTags"
                    chips
                    closable-chips
                    multiple
                    :placeholder="t('assign_tags', 'Tags')"
                    prepend-icon="mdi-tag-multiple"
                    density="compact"
                    hide-details
                    class="tag-selector"
                  >
                    <template v-slot:chip="{ props, item }">
                      <v-chip
                        v-bind="props"
                        :text="item.raw"
                        size="x-small"
                        @click:close="removeTag(file, item.raw)"
                      ></v-chip>
                    </template>
                  </v-combobox>
                </v-col>
                <v-col cols="12" sm="3" md="3" style="padding:5px">
                  <v-combobox
                    v-model="file.selectedModels"
                    :items="filteredModels"
                    item-title="id"
                    item-value="id"
                    :placeholder="t('restrict_to_models', 'Restrict to models')"
                    chips
                    multiple
                    clearable
                    closable-chips
                    density="compact"
                    hide-details
                    class="model-selector"
                    @update:modelValue="updateModels(file)"
                  >
                    <template v-slot:chip="{ props, item }">
                      <v-chip
                        v-bind="props"
                        :text="item.raw.id"
                        size="x-small"
                      ></v-chip>
                    </template>
                  </v-combobox>
                </v-col>
                <v-col cols="12" sm="2" md="2" class="text-sm-right">
                  <v-switch
                    class="active-file"
                    v-model="file.active"
                    :label="file.active ? t('active', 'Active') : t('inactive', 'Inactive')"
                    @change="updateFileContext(file)"
                    hide-details
                  ></v-switch>
                </v-col>
              </v-row>

            </v-list-item>
          </v-list>
          <v-container>
             <v-row>
                <v-col cols="11" sm="0" md="10" class="text-sm-right"></v-col>
                <v-col cols="1" sm="2" md="2" class="text-sm-right">
                  <v-btn v-if="hasNewDocuments" color="primary" @click="saveAndUpload"> {{ t('save', 'Save') }} </v-btn>
                </v-col>
              </v-row>
          </v-container>

          <!-- Chip-based Navigation -->
          <v-container max-width="90%" :style="{ textAlign: 'left', padding: '0', margin: 0, marginLeft: '35px' }">
            <v-row>
              <v-col cols="12" md="10" sm="12" style="text-align: left">
                <v-chip-group v-model="selectedTag" class="chip-navigation" column multiple>
                  <v-chip
                    v-for="(tag, index) in uniqueTags"
                    :key="index"
                    class="ma-1"
                    size="small"
                    :color="selectedTag === tag ? 'primary' : ''"
                    @click="selectTag(tag)"
                  >
                    {{ tag }}
                  </v-chip>
                </v-chip-group>
              </v-col>
              <v-col cols="2" md="2" sm="0">
                <v-btn v-if="selectedTag" color="error" @click="resetFilter">
                  {{ t('reset_filter', 'Reset Filter') }}
                </v-btn>
              </v-col>
            </v-row>
          </v-container>

          <!-- Render GripsBoxItems with DataTable -->
          <v-data-table :items="filteredGripsBoxItems" item-value="id" density="compact">
            <template v-slot:item.models="{ item }">
              <v-chip-group multiple column>
                <v-chip v-for="(model, index) in item.models" :key="index" size="x-small" class="ma-1">{{ model }}</v-chip>
              </v-chip-group>
            </template>
            <template v-slot:item.tags="{ item }">
              <v-chip-group multiple column>
                <v-chip v-for="(tag, index) in item.tags" :key="index" size="x-small" class="ma-1">{{ tag }}</v-chip>
              </v-chip-group>
            </template>
            <template v-slot:item.active="{ item }">
              <v-switch hide-details v-model="item.active" @change="updateActiveStatus(item.id, item.active)"></v-switch>
            </template>
            <template v-slot:item.actions="{ item }">
              <v-icon small @click="confirmDelete(item.id)" color="red">mdi-delete</v-icon>
            </template>
          </v-data-table>

          <!-- Confirm Delete Dialog -->
          <v-dialog v-model="confirmDeleteDialog" width="400">
            <v-card>
              <v-card-title class="headline"> {{ t('confirm_delete', 'Confirm Delete') }} </v-card-title>
              <v-card-text> {{ t('delete_confirmation_message', 'Are you sure you want to delete this item?') }} </v-card-text>
              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn color="green darken-1"  @click="deleteGripsbox(deleteId)">
                  {{ t('yes', 'Yes') }}
                </v-btn>
                <v-btn color="red darken-1"  @click="confirmDeleteDialog = false">
                  {{ t('no', 'No') }}
                </v-btn>
              </v-card-actions>
            </v-card>
          </v-dialog>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="secondary" @click="isModalOpen = false"> {{ t('close', 'Close') }} </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { postToGripsbox, getGripsBox, updateGripsBoxActiveStatus, deleteGripsBoxItem } from '@/vue/services/api.js';
import { useModelsStore } from '@/vue/stores';
import { filterModels, loadModels } from "@/vue/services/models.js";

const { t } = useI18n();
const isModalOpen = ref(false);
const files = ref([]);
const uploadedFiles = ref([]);
const availableTags = ref(['Work', 'Personal', 'Project A', 'Project B', 'Confidential', 'Public']);
const newDocuments = ref([]);
const hasNewDocuments = computed(() => newDocuments.value.length > 0);
const gripsBoxItems = ref([]);
const selectedTag = ref(null);
const filteredGripsBoxItems = ref([]);
const confirmDeleteDialog = ref(false);
const deleteId = ref(null);

// Unique tags from gripsBoxItems
const uniqueTags = computed(() => {
  const tagsSet = new Set();
  gripsBoxItems.value.forEach(item => {
    item.tags.forEach(tag => tagsSet.add(tag));
  });
  return Array.from(tagsSet);
});

// Handle tag selection and filtering
const selectTag = (tag) => {
  selectedTag.value = tag;
  filterGripsBoxItems();
};

const removeTag = (file, tag) => {
  const index = file.tags.indexOf(tag);
  if (index >= 0) file.tags.splice(index, 1);
};

const filterGripsBoxItems = () => {
  filteredGripsBoxItems.value = selectedTag.value
    ? gripsBoxItems.value.filter(item => item.tags.includes(selectedTag.value))
    : gripsBoxItems.value;
};

const updateFileContext = (file) => {
  console.log(`File ${file.name} is now ${file.active ? 'active' : 'inactive'}`);
  console.log(`Tags for ${file.name}:`, file.tags);
  console.log(`Selected models for ${file.name}:`, file.selectedModels);
};

// Reset filter functionality
const resetFilter = () => {
  selectedTag.value = null;
  filteredGripsBoxItems.value = gripsBoxItems.value;
};

const handleFileUpload = () => {
  newDocuments.value = files.value.map(file => ({
    file: file,
    name: file.name,
    size: file.size,
    type: file.type,
    active: true,
    tags: [],
    selectedModels: []
  }));
  uploadedFiles.value.push(...newDocuments.value);
};

const updateActiveStatus = async (id, active) => {
  try {
    await updateGripsBoxActiveStatus(id, active);
    console.log(`Active status for item ${id} updated to ${active}`);
  } catch (error) {
    console.error('Failed to update active status:', error);
  }
};

const confirmDelete = (id) => {
  deleteId.value = id;
  confirmDeleteDialog.value = true;
};

const deleteGripsbox = async (id) => {
  try {
    await deleteGripsBoxItem(id);
    filteredGripsBoxItems.value = filteredGripsBoxItems.value.filter(item => item.id !== id);
    console.log(`Item ${id} deleted successfully.`);
  } catch (error) {
    console.error('Failed to delete gripsbox:', error);
  } finally {
    confirmDeleteDialog.value = false; // Close the dialog
  }
};

const uploadSingleFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file.file);
  formData.append('name', file.name);
  formData.append('size', file.size);
  formData.append('type', file.type);
  formData.append('active', file.active);
  formData.append('tags', JSON.stringify(file.tags));
  formData.append('models', JSON.stringify(file.selectedModels.map(item => item.id)));
  return await postToGripsbox(formData);
};

const saveAndUpload = async () => {
  let successCount = 0;
  let errorCount = 0;

  for (const file of newDocuments.value) {
    try {
      const result = await uploadSingleFile(file);
      console.log('File uploaded successfully:', result);
      successCount++;
    } catch (error) {
      console.error('Error uploading file:', file.name, error);
      errorCount++;
    }
  }

  if (successCount > 0) {
    window.dispatchEvent(new CustomEvent('show-message', {
      detail: {
        color: 'success',
        message: t('files_uploaded_successfully', `${successCount} file(s) uploaded successfully.`)
      }
    }));
  }
  if (errorCount > 0) {
    window.dispatchEvent(new CustomEvent('show-message', {
      detail: {
        color: 'error',
        message: t('error_uploading_files', `Failed to upload ${errorCount} file(s). Please try again.`)
      }
    }));
  }

  // Clear documents and close modal if all files uploaded successfully
  if (successCount > 0 && errorCount === 0) {
    newDocuments.value = [];
    uploadedFiles.value=[]
    files.value=null
  }
  loadGripspbox();
};

const modelsStore = useModelsStore();
const models = ref([]);
const filteredModels = ref([]);
const selectedCategory = ref('');

const loadAndFilterModels = async () => {
  await modelsStore.loadFromStorage();
  models.value = await loadModels();
  onCategoryChange(selectedCategory.value);
};

const onCategoryChange = (category) => {
  filteredModels.value = filterModels(models.value, category);
};

const updateModels = (file) => {
  console.log(`Updated selected models for ${file.name}:`, file.selectedModels);
};

async function loadGripspbox() {
  const response = await getGripsBox();
  gripsBoxItems.value = response.map(item => ({
    id: item.id,
    name: item.name,
    size: item.size,
    active: item.active,
    tags: item.tags,
    models: item.models,
    created: item.created,
    actions: []
  }));
  filteredGripsBoxItems.value = gripsBoxItems.value;
}

onMounted(async () => {
  loadAndFilterModels();
  loadGripspbox();
});
</script>

<style scoped>
.contextmanager-opener {
  margin-top: -25px;
}

.tag-selector :deep(.v-field__input),
.model-selector :deep(.v-field__input) {
  min-height: 32px;
  padding-top: 0;
  padding-bottom: 0;
}

.tag-selector :deep(.v-chip),
.model-selector :deep(.v-chip) {
  margin-top: 2px;
  margin-bottom: 2px;
}

.active-file {
  margin-left: 10px;
}

/* Chip-based Navigation */
.chip-navigation {
  width: 60%;
  height: 100px;
  margin-bottom: 20px;
  overflow-x: auto;
}
</style>
