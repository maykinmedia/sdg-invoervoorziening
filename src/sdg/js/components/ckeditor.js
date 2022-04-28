import ClassicEditorBase from '@ckeditor/ckeditor5-editor-classic/src/classiceditor';
import EssentialsPlugin from '@ckeditor/ckeditor5-essentials/src/essentials';
import UploadAdapterPlugin from '@ckeditor/ckeditor5-adapter-ckfinder/src/uploadadapter';
import AutoformatPlugin from '@ckeditor/ckeditor5-autoformat/src/autoformat';
import BoldPlugin from '@ckeditor/ckeditor5-basic-styles/src/bold';
import ItalicPlugin from '@ckeditor/ckeditor5-basic-styles/src/italic';
import BlockQuotePlugin from '@ckeditor/ckeditor5-block-quote/src/blockquote';
import HeadingPlugin from '@ckeditor/ckeditor5-heading/src/heading';
import LinkPlugin from '@ckeditor/ckeditor5-link/src/link';
import ListPlugin from '@ckeditor/ckeditor5-list/src/list';
import ParagraphPlugin from '@ckeditor/ckeditor5-paragraph/src/paragraph';
import MarkdownPlugin from '@ckeditor/ckeditor5-markdown-gfm/src/markdown';
import Table from '@ckeditor/ckeditor5-table/src/table';
import TableToolbar from '@ckeditor/ckeditor5-table/src/tabletoolbar';
import Indent from '@ckeditor/ckeditor5-indent/src/indent'
import IndentBlock from '@ckeditor/ckeditor5-indent/src/indentblock'

export default class ClassicEditor extends ClassicEditorBase {
}

ClassicEditor.builtinPlugins = [
    MarkdownPlugin,
    EssentialsPlugin,
    UploadAdapterPlugin,
    AutoformatPlugin,
    BoldPlugin,
    ItalicPlugin,
    BlockQuotePlugin,
    HeadingPlugin,
    LinkPlugin,
    ListPlugin,
    ParagraphPlugin,
    Table,
    TableToolbar,
    Indent,
    IndentBlock
];

ClassicEditor.defaultConfig = {
    heading: {
        options: [
            {model: 'paragraph', title: 'Paragraaf', class: 'ck-heading_paragraph'},
            {model: 'heading2', view: 'h3', title: 'Kop 3', class: 'ck-heading_heading2'},
            {model: 'heading3', view: 'h4', title: 'Kop 4', class: 'ck-heading_heading3'}
        ]
    },
    toolbar: {
        items: [
            'heading',
            '|',
            'bold',
            'italic',
            'link',
            'bulletedList',
            'numberedList',
            'insertTable',
            'blockQuote',
            'outdent',
            'indent',
            'undo',
            'redo',
        ]
    },
    table: {
        contentToolbar: ['tableColumn', 'tableRow'],
        defaultHeadings: {rows: 1},
    },
    language: 'nl',
};
