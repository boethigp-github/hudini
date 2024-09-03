<template>
  <a-drawer
      :title="$t('model_comparison', 'model comparison')"
      placement="right"
      :visible="drawerVisible"
      @close="closeDrawer"
      :width="width"
  >

    <div v-if="comparisonData.length > 0">
      <!-- Search inputs -->
<!--      <div class="search-fields">-->
<!--        <a-input-->
<!--            placeholder="Search Model"-->
<!--            v-model="searchTerms.model"-->
<!--            @input="filterData"-->
<!--            style="margin-bottom: 8px;"-->
<!--        />-->
<!--        <a-input-->
<!--            placeholder="Search Content"-->
<!--            v-model="searchTerms.content"-->
<!--            @input="filterData"-->
<!--            style="margin-bottom: 8px;"-->
<!--        />-->
<!--        <a-input-->
<!--            placeholder="Search Timestamp"-->
<!--            v-model="searchTerms.timestamp"-->
<!--            @input="filterData"-->
<!--            style="margin-bottom: 8px;"-->
<!--        />-->
<!--        <a-input-->
<!--            placeholder="Search Error"-->
<!--            v-model="searchTerms.error"-->
<!--            @input="filterData"-->
<!--        />-->
<!--      </div>-->
      <a-table
          bordered
          size="small"
          :dataSource="comparisonData"
          :columns="columns"
          rowKey="model"
          :pagination="false"
          :rowClassName="getRowClass"
      >
        <template  v-slot:bodyCell="{ record, column, index }">
          <VueMarkdownIT style="margin-top:11px" v-if="column.dataIndex==='content'"  :breaks="true" :plugins="plugins" :source="record.content" />
          <div v-else>
            {{record[column.dataIndex]}}
          </div>
        </template>
      </a-table>
    </div>
    <div v-else>
      No data to compare.
    </div>
  </a-drawer>
</template>

<script>
import {defineComponent, onBeforeUnmount, onMounted, ref} from 'vue';
import { Drawer, Table } from 'ant-design-vue';
import Markdown from 'vue3-markdown-it';
import { useI18n } from 'vue-i18n';

export default defineComponent({
  name: 'ComparisonDrawer',
  components: {
    'a-drawer': Drawer,
    'a-table': Table,
    'VueMarkdownIT': Markdown,
  },
  props: {
    comparisonData: {
      type: Array,
      required: true,
      default: () => [],
    },
    plugins: {
      type: Array,
      required: true,
      default: () => [],
    },
    width: {
      type: String,
      required: false,
      default: '500px',
    },
  },
  setup(props) {
    const { t } = useI18n();
    const closeDrawer = ()=>{
      const event = new CustomEvent("comparison-close", {  });
      window.dispatchEvent(event);
    }
    const searchTerms = ref({
      model: '',
      content: '',
      timestamp: '',
      error: ''
    });


    const filterData = () => {
      // Filtering logic handled by computed property
    };

    const closeComparison = () => {
      drawerVisible.value = false;
    };

    const openComparison = () => {
      drawerVisible.value = true;
    };

    const getRowClass = (record, index) => {
      return record.model === 'UserPrompt' ? 'userpromptrow' : 'compare-row';
    };


    // Handle event listeners in lifecycle hooks
    onMounted(() => {
      window.addEventListener("comparison-close", closeComparison);
      window.addEventListener("comparison-open", openComparison);
    });

    onBeforeUnmount(() => {
      window.removeEventListener("comparison-close", closeComparison);
      window.removeEventListener("comparison-open", openComparison);
    });

    let drawerVisible = ref(false)

    const columns = ref([
      {
        title: t('model'),
        dataIndex: 'model',
        key: 'model',
        width: 300,
      },
      {
        title: t('content'),
        dataIndex: 'content',
        key: 'content',
      },
      {
        title: t('timestamp'),
        dataIndex: 'timestamp',
        key: 'timestamp',
        width: 170,
      },
      {
        title: t('error'),
        dataIndex: 'error',
        key: 'error',
        width: 100,
      },
    ]);

    return {
      columns,
      plugins: props.plugins,
      closeDrawer,
      drawerVisible,
      getRowClass,
      searchTerms,
      filterData
    };
  },
});
</script>
<style >

.userpromptrow {
  background: #e7e7e7 !important;
  font-weight: bold;
}

.compare-row{
  vertical-align: top!important;
}
</style>
