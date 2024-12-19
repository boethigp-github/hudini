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
            {{item.active}}
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
            {{
              formMode === 'create' ? t('create_parameter', 'Create Parameter') : t('update_parameter', 'Update Parameter')
            }}
          </v-card-title>
          <v-card-text>
            <v-form ref="form">


              <v-select
                  v-model="formData.parameter"
                  :items="parameterOptions"
                  :label="t('parameter', 'Parameter')"
                  :rules="[requiredRule]"
                  item-value="value"
                  item-text="title"
              />
              <v-select
                  v-model="formData.model"
                  :items="availableModels.map(item => item.id)"
                  :label="t('model', 'Model')"
                  :rules="[requiredRule]"
                  clearable
              />
              <v-textarea
                  v-model="formData.value"
                  :label="t('value', 'Value')"
                  :rules="[valueRequiredRule]"
              />

              <v-switch
                  v-model="formData.active"
                  :label="t('active', 'Active')"
              />
            </v-form>
          </v-card-text>
          <v-card-actions>
            <v-spacer/>
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
            {{
              t('delete_confirmation_message', 'Are you sure you want to delete this parameter? This action cannot be undone.')
            }}
          </v-card-text>
          <v-card-actions>
            <v-spacer/>
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
import {ref, reactive, onMounted} from "vue";
import {useI18n} from "vue-i18n";
import {getModelParameters, createModelParameter, updateModelParameter, deleteModelParameter} from "@/vue/services/api.js";
import {useModelsStore} from "@/vue/stores/models";

export default {
  setup() {
    const {t} = useI18n();
    const modelsStore = useModelsStore();

    const form = ref(null);
    const parameters = ref([]);
    const isFormOpen = ref(false);
    const isDeleteDialogOpen = ref(false);
    const formMode = ref("create");
    const availableModels = ref([]);
    const formData = ref({
      uuid: null,
      parameter: "",
      model: "",
      value: "",
      active: false,
    });
    const deleteUuid = ref(null);

    const parameterOptions = [
      {text: "systemprompt", title: t("system_prompt", "System Prompt")},
      {value: "temperature", title: t("temperature", "Temperature")},
      {value: "penalty", title: t("penalty", "Penalty")},
    ];

    const requiredRule = (v) => !!v || t("field_required", "Field is required");
    const valueRequiredRule = (v) => (!!v && v.trim() !== "") || t("field_required", "Field is required");

    const loadModels = async () => {
      await modelsStore.loadFromStorage();
      availableModels.value = await modelsStore.getServiceResponse();
    };

    const fetchParameters = async () => {
      try {
        parameters.value = await getModelParameters();
      } catch (error) {
        console.error("Failed to load model parameters:", error);
      }
    };

    const saveParameter = () => {

      form.value?.validate().then(async (result) => {

        if (!result.valid) {
          console.error("Form validation failed");
          return;
        }

      const payload = {
        parameter: formData.value.parameter,
        model:  formData.value.model,
        value: { key:  formData.value.parameter, value:  formData.value.value },
        active:  formData.value.active,
      };

        if ( !formData.value.uuid) {
          await createNewModelParameter(payload);
        } else {

          console.log(" formData.value",  formData.value);
              console.log("update:", result.valid)
          await updateModelParameter( formData.value.uuid, payload);
        }

        await fetchParameters();
        closeForm();
      })

    };

    const closeForm = () => {
      isFormOpen.value = false;
    };

    const editParameter = (item) => {
      openForm("update", item);
    };

    const openForm = (mode = "create", data = null) => {
      formMode.value = mode;

      if (mode === "update" && data) {
        formData.value.uuid = data.uuid;
        formData.value.parameter = data.parameter;
        formData.value.model = data.model;
        formData.value.value = data.value.value;
        formData.value.active = data.active;
      } else {
        formData.value.uuid = null;
        formData.value.parameter = "";
        formData.value.model = "";
        formData.value.value = "";
        formData.value.active = false;
      }

      isFormOpen.value = true;
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


    const toggleActiveModelParameter = async (uuid, active) => {
      console.log(`Toggling active state for parameter: ${uuid} to ${active}`);
      // Add your API logic here for toggling the active state
    };

    onMounted(async () => {
      await fetchParameters();
      await loadModels();
    });

    const createNewModelParameter = async (payload) => {


      await createModelParameter(payload);
    };

    const updateParameter = async (uuid, data) => {
 await u
    };

        const headers = [
      { title: t('uuid', 'UUID'), key: "uuid" },
      { title: t('parameter', 'Parameter'), key: "parameter" },
      { title: t('active', 'Active'), key: "active" },
      { title: t('actions', 'Actions'), key: "actions", sortable: false },
    ];


    return {
      t,
      form,
      parameters,
      isFormOpen,
      isDeleteDialogOpen,
      formMode,
      formData,
      headers,
      deleteUuid,
      parameterOptions,
      availableModels,
      requiredRule,
      valueRequiredRule,
      saveParameter,
      closeForm,
      editParameter,
      openForm,
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
