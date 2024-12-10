<template>
  <div>
    <v-card>
      <v-card-text>
        <!-- Add New Parameter Button -->
        <v-btn style="float: right" color="primary" @click="openForm('create')">
          {{ t('add_new_parameter', 'Add New Parameter') }}
        </v-btn>

        <!-- Model Parameters Data Table -->
        <v-data-table
          :items="parameters"
          :headers="headers"
          density="compact"
          item-value="uuid"
          class="mt-4"
        >
          <template v-slot:[`item.uuid`]="{ item }">
            {{ item.uuid }}
          </template>

          <template v-slot:[`item.parameter`]="{ item }">
            {{ item.parameter }}
          </template>

          <template v-slot:[`item.value`]="{ item }">
            {{ item.value.key }}: {{ item.value.value }}
          </template>

          <template v-slot:[`item.active`]="{ item }">
            <v-switch
              style="margin-top: 15px"
              density="compact"
              v-model="item.active"
              @change="toggleActive(item.uuid, item.active)"
            />
          </template>

          <template v-slot:[`item.actions`]="{ item }">
            <v-btn variant="flat" density="compact" icon @click="editParameter(item)">
              <v-icon>mdi-pencil</v-icon>
            </v-btn>
            <v-btn
              density="compact"
              variant="flat"
              icon
              color="red"
              @click="openDeleteDialog(item.uuid)"
            >
              <v-icon>mdi-delete</v-icon>
            </v-btn>
          </template>
        </v-data-table>
      </v-card-text>

      <!-- Parameter Form Dialog -->
      <v-dialog v-model="isFormOpen" max-width="600px">
        <v-card>
          <v-card-title>
            {{ formMode === 'create' ? t('create_parameter', 'Create Parameter') : t('update_parameter', 'Update Parameter') }}
          </v-card-title>
          <v-card-text>
            <v-form ref="form">
              <v-text-field
                v-model="formData.parameter"
                :label="t('parameter', 'Parameter')"
                :rules="[requiredRule]"
              />
              <v-text-field
                v-model="formData.model"
                :label="t('model', 'Model')"
                :rules="[requiredRule]"
              />
              <v-textarea
                v-model="formData.value"
                :label="t('value', 'Value')"
              />
              <v-switch
                v-model="formData.active"
                :label="t('active', 'Active')"
              />
            </v-form>
          </v-card-text>
          <v-card-actions>
            <v-spacer />
            <v-btn color="green" @click="saveParameter">
              {{ t('save', 'Save') }}
            </v-btn>
            <v-btn color="red" @click="closeForm">
              {{ t('cancel', 'Cancel') }}
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <!-- Delete Confirmation Dialog -->
      <v-dialog v-model="isDeleteDialogOpen" max-width="500px">
        <v-card>
          <v-card-title>
            {{ t('confirm_delete', 'Confirm Delete') }}
          </v-card-title>
          <v-card-text>
            {{ t('delete_confirmation_message', 'Are you sure you want to delete this parameter? This action cannot be undone.') }}
          </v-card-text>
          <v-card-actions>
            <v-spacer />
            <v-btn color="red" @click="confirmDelete">
              {{ t('delete', 'Delete') }}
            </v-btn>
            <v-btn color="grey" @click="isDeleteDialogOpen = false">
              {{ t('cancel', 'Cancel') }}
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-card>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from "vue";
import { useI18n } from "vue-i18n";

export default {
  setup() {
    const { t } = useI18n();

    // Reactive State
    const parameters = ref([]);
    const isFormOpen = ref(false);
    const isDeleteDialogOpen = ref(false);
    const formMode = ref("create"); // "create" or "update"
    const formData = reactive({
      uuid: null,
      parameter: "",
      model: "",
      value: "",
      active: false,
    });
    const deleteUuid = ref(null);

    // Data Table Headers
    const headers = [
      { text: t('uuid', 'UUID'), key: "uuid" },
      { text: t('parameter', 'Parameter'), key: "parameter" },
      { text: t('value', 'Value'), key: "value" },
      { text: t('active', 'Active'), key: "active" },
      { text: t('actions', 'Actions'), key: "actions", sortable: false },
    ];

    // Placeholder API calls
    const getModelParameters = async () => [
      { uuid: "1", parameter: "param1", model: "model1", value: { key: "parameter1", value: "testvalue" }, active: true },
    ];
    const createModelParameter = async (data) => console.log("Creating", data);
    const updateModelParameter = async (uuid, data) => console.log("Updating", uuid, data);
    const deleteModelParameter = async (uuid) => console.log("Deleting", uuid);
    const toggleActiveModelParameter = async (uuid, active) => console.log("Toggling Active", uuid, active);

    // Form Validation
    const requiredRule = (v) => !!v || t('field_required', 'Field is required');

    // Methods
    const fetchParameters = async () => {
      parameters.value = await getModelParameters();
    };

const openForm = (mode = "create", data = null) => {
  formMode.value = mode; // Explicitly set the form mode

  if (mode === "update" && data) {
    // Populate form with existing data for updating
    formData.uuid = data.uuid;
    formData.parameter = data.parameter;
    formData.model = data.model;
    formData.value = JSON.stringify(data.value, null, 2);
    formData.active = data.active;
  } else {
    // Reset form for creating new parameter
    formData.uuid = null;
    formData.parameter = "";
    formData.model = "";
    formData.value = "";
    formData.active = false;
  }

  isFormOpen.value = true; // Open the form dialog
};

    const closeForm = () => {
      isFormOpen.value = false;
    };

    const saveParameter = async () => {
      const payload = {
        parameter: formData.parameter,
        model: formData.model,
        value: { key: formData.parameter, value: formData.value },
        active: formData.active,
      };

      if (formMode.value === "create") {
        await createModelParameter(payload);
      } else {
        await updateModelParameter(formData.uuid, payload);
      }

      await fetchParameters();
      closeForm();
    };

    const editParameter = (item) => {
      openForm("update", item);
    };

    const openDeleteDialog = (uuid) => {
      deleteUuid.value = uuid;
      isDeleteDialogOpen.value = true;
    };

    const confirmDelete = async () => {
      await deleteModelParameter(deleteUuid.value);
      await fetchParameters();
      isDeleteDialogOpen.value = false;
    };

    const toggleActive = async (uuid, active) => {
      await toggleActiveModelParameter(uuid, active);
      await fetchParameters();
    };

    // Lifecycle
    onMounted(fetchParameters);

    // Return all reactive properties and methods
    return {
      t,
      parameters,
      isFormOpen,
      isDeleteDialogOpen,
      formMode,
      formData,
      headers,
      deleteUuid,
      requiredRule,
      openForm,
      closeForm,
      saveParameter,
      editParameter,
      openDeleteDialog,
      confirmDelete,
      toggleActive,
    };
  },
};
</script>

<style scoped>
.mt-4 {
  margin-top: 1rem;
}
</style>
