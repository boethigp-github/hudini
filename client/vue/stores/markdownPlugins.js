// markdown-plugins.js

import MarkdownIt from 'markdown-it';
import MarkdownItHighlightJs from 'markdown-it-highlightjs';
import MarkdownItStrikethroughAlt from 'markdown-it-strikethrough-alt';
import MarkdownItAbbr from 'markdown-it-abbr';
import MarkdownItAnchor from 'markdown-it-anchor';
import MarkdownItDefList from 'markdown-it-deflist';
import MarkdownItFootnote from 'markdown-it-footnote';
import MarkdownItIns from 'markdown-it-ins';
import MarkdownSub from 'markdown-it-sub';
import MarkdownSup from 'markdown-it-sup';
import MarkdownTaskList from 'markdown-it-task-lists';
import MarkdownMark from 'markdown-it-mark';
import MarkdownCollapsible from 'markdown-it-collapsible';
import MarkdownCheckbox from 'markdown-it-checkbox';
import MarkdownTocDoneRight from 'markdown-it-toc-done-right';

export const markdownPlugins = [
  { plugin: MarkdownItHighlightJs },
  { plugin: MarkdownItStrikethroughAlt },
  { plugin: MarkdownIt },
  { plugin: MarkdownItAbbr },
  { plugin: MarkdownItAnchor },
  { plugin: MarkdownItDefList },
  { plugin: MarkdownItFootnote },
  { plugin: MarkdownItIns },
  { plugin: MarkdownSub },
  { plugin: MarkdownSup },
  { plugin: MarkdownTaskList },
  { plugin: MarkdownTocDoneRight },
  { plugin: MarkdownMark },
  { plugin: MarkdownCollapsible },
  { plugin: MarkdownCheckbox },
];

// You can add configuration for specific plugins here if needed
// For example:
// export const markdownConfig = {
//   [MarkdownItAnchor.name]: {
//     permalink: true,
//     permalinkBefore: true,
//     permalinkSymbol: '¶'
//   },
//   // ... other plugin configs
// };

export default markdownPlugins;