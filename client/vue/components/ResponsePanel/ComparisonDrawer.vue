<template>
  <a-drawer
      title="Response Comparison"
      placement="right"
      :visible="drawerVisible"
      @close="closeDrawer"
      :width="width"
  >
    <div v-if="comparisonData.length > 0">
      <a-table
          bordered
          size="small"
          :dataSource="comparisonData"
          :columns="columns"
          rowKey="model"
          :pagination="false"
          :rowClassName="getRowClass"
      >
        <!-- Define body cells for the 'model' column -->
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

    const closeDrawer = ()=>{
      const event = new CustomEvent("comparison-close", {  });
      window.dispatchEvent(event);
    }

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

    const columns = [
      {
        title: 'Model / Prompt',
        dataIndex: 'model',
        key: 'model',
        width:300

      },
      {
        title: 'Content',
        dataIndex: 'content',
        key: 'content',

      },
      {
        title: 'Timestamp',
        dataIndex: 'timestamp',
        key: 'timestamp',
        width: 170
      },
      {
        title: 'Error',
        dataIndex: 'error',
        key: 'error',
        width: 100
      },
    ];

    return {
      columns,
      plugins: props.plugins,
      closeDrawer,
      drawerVisible,
      getRowClass
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
