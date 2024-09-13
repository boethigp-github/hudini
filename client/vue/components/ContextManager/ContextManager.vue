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

    <v-dialog v-model="isModalOpen" max-width="90%">
      <v-card>
        <v-card-title>
          {{ t('Hudinis Gripsbox', 'Hudinis Gripsbox') }}
        </v-card-title>
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
                <v-col cols="12" sm="4" md="3">
                  <v-list-item-title class="text-truncate">
                    <v-icon start icon="mdi-file" size="small"></v-icon>
                    {{ file.name }}
                  </v-list-item-title>
                  <v-list-item-subtitle class="text-truncate">{{ file.size }} bytes</v-list-item-subtitle>
                </v-col>
                <v-col cols="12" sm="5" md="5">
                  <v-combobox
                    v-model="file.tags"
                    :items="availableTags"
                    chips
                    closable-chips
                    multiple
                    :label="t('assign_tags', 'Tags')"
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
                <v-col cols="12" sm="3" md="4" class="text-sm-right">
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
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn v-if="hasNewDocuments" color="primary" @click="saveAndUpload">
            {{ t('save', 'Save') }}
          </v-btn>
          <v-btn color="secondary" @click="isModalOpen = false">
            {{ t('close', 'Close') }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
const isModalOpen = ref(false);
const files = ref([]);
const uploadedFiles = ref([]);
const availableTags = ref(['Work', 'Personal', 'Project A', 'Project B', 'Confidential', 'Public']);
const newDocuments = ref([]);

const hasNewDocuments = computed(() => newDocuments.value.length > 0);

const handleFileUpload = () => {
  newDocuments.value = files.value.map(file => ({
    file: file,
    name: file.name,
    size: file.size,
    type: file.type,
    active: true,
    tags: []
  }));
  uploadedFiles.value = [...uploadedFiles.value, ...newDocuments.value];
};

const updateFileContext = (file) => {
  console.log(`File ${file.name} is now ${file.active ? 'active' : 'inactive'}`);
  console.log(`Tags for ${file.name}:`, file.tags);
};

const removeTag = (file, tag) => {
  const index = file.tags.indexOf(tag);
  if (index >= 0) file.tags.splice(index, 1);
};

const uploadSingleFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file.file);
  formData.append('metadata', JSON.stringify({
    name: file.name,
    size: file.size,
    type: file.type,
    active: file.active,
    tags: file.tags
  }));

  const response = await fetch('/gripsbox', {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return await response.json();
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

  if (successCount > 0 && errorCount === 0) {
    newDocuments.value = []; // Clear new documents only if all uploads were successful
    isModalOpen.value = false; // Close the modal
  }
};
</script>

<style scoped>
.contextmanager-opener {
  margin-top: -20px;
}

.tag-selector :deep(.v-field__input) {
  min-height: 32px;
  padding-top: 0;
  padding-bottom: 0;
}

.tag-selector :deep(.v-chip) {
  margin-top: 2px;
  margin-bottom: 2px;
}

.active-file {
  margin-left: 10px;
}
</style>