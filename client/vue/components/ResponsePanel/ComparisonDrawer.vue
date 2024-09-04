<template>
  <a-drawer
    :title="$t('model_comparison', 'model comparison')"
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
        <template v-slot:bodyCell="{ record, column, index }">
          <VueMarkdownIT
            v-if="column.dataIndex === 'content'"
            style="margin-top:11px"
            :breaks="true"
            :plugins="plugins"
            :source="record.content"
          />
          <div v-else-if="column.dataIndex === 'statistics'">
            <a-list
              v-if="record.rawData?.completion?.usage"
              :dataSource="[record.rawData.completion.usage]"
              :bordered="false"
              size="small"
            >
              <template #renderItem="{ item }">
                <a-list-item size="small">
                  <a-list-item-meta>
                    <template #title>
                      <a-statistic
                        :title="$t('completion_tokens', 'Completion Tokens')"
                        :value="item.completion_tokens"
                      />
                      <a-statistic
                        :title="$t('prompt_tokens', 'Prompt Tokens')"
                        :value="item.prompt_tokens"
                      />
                      <a-statistic
                        :title="$t('all_tokens', 'All Tokens')"
                        :value="item.total_tokens"
                      />
                      <a-statistic
                        :title="$t('run_time', 'Run Time')"
                        :value="formatDuration(item.started, item.ended)"
                      />
                    </template>
                  </a-list-item-meta>
                </a-list-item>
              </template>
            </a-list>
          </div>
          <div v-else>
            {{ record[column.dataIndex] }}
          </div>
        </template>
      </a-table>
    </div>
    <div v-else>
      {{ $t('no_data_to_compare', 'No data to compare.') }}
    </div>
  </a-drawer>
</template>

<script>
import { defineComponent, onBeforeUnmount, onMounted, ref } from 'vue';
import { Drawer, Table, List, Statistic } from 'ant-design-vue';
import Markdown from 'vue3-markdown-it';
import { useI18n } from 'vue-i18n';
import { RobotOutlined, UserOutlined } from '@ant-design/icons-vue';

export default defineComponent({
  name: 'ComparisonDrawer',
  components: {
    UserOutlined,
    RobotOutlined,
    'a-drawer': Drawer,
    'a-table': Table,
    'a-list': List,
    'a-statistic': Statistic,
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
    const closeDrawer = () => {
      const event = new CustomEvent('comparison-close', {});
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

const formatTimestamp = (timestamp) => {
  if (!timestamp) return '';
  const date = new Date(timestamp); // Convert milliseconds to Date object
  return date.toLocaleString([], {

    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  }); // Format as readable date-time string with seconds
};

    const formatDuration = (start, end) => {
      const duration = end - start;
      const seconds = ((duration % 60000)).toFixed(0);
      return `${seconds} ms`;
    };

    onMounted(() => {
      window.addEventListener('comparison-close', closeComparison);
      window.addEventListener('comparison-open', openComparison);
    });

    onBeforeUnmount(() => {
      window.removeEventListener('comparison-close', closeComparison);
      window.removeEventListener('comparison-open', openComparison);
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
        title: t('statistics', 'Statistics'),
        dataIndex: 'statistics',
        key: 'statistics',
        width: 220,
      },
      {
        title: t('timestamp'),
        dataIndex: 'timestamp',
        key: 'timestamp',
        width: 170,
      },
    ]);

    return {
      columns,
      plugins: props.plugins,
      closeDrawer,
      drawerVisible,
      getRowClass,
      searchTerms,
      filterData,
      formatTimestamp,
      formatDuration
    };
  },
});
</script>

<style>
.userpromptrow {
  background: #e7e7e7 !important;
  font-weight: bold;
}

.compare-row {
  vertical-align: top !important;
}
</style>
