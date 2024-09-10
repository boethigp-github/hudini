<template>
  <v-card-title>{{ $t('model_comparison', 'Model Comparison') }}</v-card-title>
  <v-card-text v-if="processedData.length">
    <v-data-table
      :headers="headers"
      :items="processedData"
      item-value="uuid"
      fixed-header
      height="61vh"
      :row-props="getRowProps"
      class="comparison-table">
      <template v-slot:item.completionContent="{ item }">
        <template v-if="item.isPrompt">
          {{ item.content }}
        </template>
        <template v-else>
          <div class="completion-content">
            <Markdown
              class="bot-answer-md"
              :breaks="true"
              :plugins="markdownPlugins"
              :source="item.content"
            />
          </div>
        </template>
      </template>
    </v-data-table>
  </v-card-text>
  <v-card-text v-else>
    {{ $t('no_data_to_compare', 'No data to compare.') }}
  </v-card-text>
</template>

<script>
import {computed, onBeforeUnmount, onMounted, ref} from 'vue';
import {useI18n} from 'vue-i18n';
import Markdown from 'vue3-markdown-it';
import {markdownPlugins} from './../../stores/markdownPlugins.js';

export default {
  name: 'ComparisonDrawer',
  components: {
    Markdown
  },
  props: {
    userContextList: {
      type: Array,
      required: true,
      default: () => [],
    },
    width: {
      type: [Number, String],
      default: 500,
    },
  },
  setup(props) {
    const { t } = useI18n();
    const drawerVisible = ref(false);

const headers = [
  {
    title: t('model'),
    align: 'start',
    key: 'model',
    width: '15%',
    
  },
  {
    title: t('completion_content', 'Completion Content'),
    align: 'start',
    key: 'completionContent',
    width: '50%',
    
  },
  {
    title: t('prompt_tokens'),
    align: 'end',
    key: 'promptTokens',
    width: '10%',
    
  },
  {
    title: t('completion_tokens'),
    align: 'end',
    key: 'completionTokens',
    width: '10%',
    
  },
  {
    title: t('total_tokens'),
    align: 'end',
    key: 'totalTokens',
    width: '10%',
    
  },
  {
    title: t('run_time') + " in ms",
    align: 'end',
    key: 'runTime',
    width: '5%',
    
  },
];
    const getRowProps = (item) => {
      return {
        class: item.item.isPrompt ? 'user-prompt-row text-primary' : 'completion-row'
      };
    };
    const processedData = computed(() => {
      return props.userContextList.flatMap(item => {
        const promptRow = {
          isPrompt: true,
          model: t('user_prompt', 'UserPrompt'),
          content: item.prompt.prompt,
          uuid: `prompt-${item.uuid}`,
          promptTokens: '-',
          completionTokens: '-',
          totalTokens: '-',
          runTime: '-'
        };
        const responseRows = (item.prompt.context_data || []).map(data => ({
          isPrompt: false,
          model: data.model,
          content: data.completion?.choices[0]?.message?.content || '',
          promptTokens: data.completion?.usage?.prompt_tokens || 0,
          completionTokens: data.completion?.usage?.completion_tokens || 0,
          totalTokens: data.completion?.usage?.total_tokens || 0,
          runTime: formatDuration(data.completion?.usage?.started, data.completion?.usage?.ended),
          uuid: data.id,
        }));
        return [promptRow, ...responseRows];
      });
    });

const formatDuration = (start, end) => {
  if (!start || !end) return '';
  return end - start;
};

    const closeDrawer = () => {
      drawerVisible.value = false;
      window.dispatchEvent(new CustomEvent('comparison-close'));
    };

    onMounted(() => {
      window.addEventListener('comparison-open', () => drawerVisible.value = true);
      window.addEventListener('comparison-close', () => drawerVisible.value = false);
    });

    onBeforeUnmount(() => {
      window.removeEventListener('comparison-open', () => drawerVisible.value = true);
      window.removeEventListener('comparison-close', () => drawerVisible.value = false);
    });

    return {
      drawerVisible,
      headers,
      processedData,
      closeDrawer,
      markdownPlugins,
      getRowProps
    };
  },
};
</script>

<style scoped>
.comparison-table :deep(td) {
  vertical-align: top !important;
}

.completion-content, .user-prompt {
  width: 100%;
  max-width: 100%;
  overflow-x: auto;
}

.bot-answer-md {
  font-size: 14px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans', sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol', 'Noto Color Emoji';
}
/* Use :deep selector to apply styles to dynamically generated rows */
/* Gradient background for user prompt rows */
:deep(.user-prompt-row td) {
  background: linear-gradient(180deg, #1e1e1e, #333333) !important; /* Dark grey to light grey gradient from top to bottom */
  font-weight: bold;
}

</style>