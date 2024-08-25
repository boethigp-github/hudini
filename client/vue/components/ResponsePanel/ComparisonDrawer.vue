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
          :dataSource="comparisonData.filter(item => item.model)"
          :columns="columns"
          rowKey="model"
          pagination={false}
      >
        <template #content="{ text }">
          <VueMarkdownIT :breaks="true" :plugins="plugins" :source="text" />
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
        title: 'Model',
        dataIndex: 'model',
        key: 'model',
      },
      {
        title: 'Response Content',
        dataIndex: 'content',
        key: 'content',
        slots: { customRender: 'content' },  // Use slots for custom rendering
      },
      {
        title: 'Timestamp',
        dataIndex: 'timestamp',
        key: 'timestamp',
      },
      {
        title: 'Error',
        dataIndex: 'error',
        key: 'error',
      },
    ];

    return {
      columns,
      plugins: props.plugins,
      closeDrawer,
      drawerVisible
    };
  },
});
</script>
