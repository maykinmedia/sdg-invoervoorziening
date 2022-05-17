import {Component} from './abstract/component';
import ClassicEditor from './ckeditor';


/** @type {NodeListOf<HTMLTextAreaElement>} */
const MARKDOWN_EDITORS = document.querySelectorAll('.markdownx textarea');
const GENERIC_EDITOR_LOCK = Symbol('generic-editor-lock');


class MarkdownEditor extends Component {
    /**
     * Binds events to callbacks.
     * Use this to define EventListeners, MutationObservers etc.
     */
    bindEvents() {
        const observer = new MutationObserver(() => {
            this.setState({readOnly: this.node.readOnly});
        });
        observer.observe(this.node, {
            attributes: true,
            childList: true,
            subtree: true
        });
    }

    /**
     * Returns the editors value.
     * @return {string}
     */
    getValue() {
        return this.editor?.getData() || '';
    }

    /**
     * Sets the editors value.
     * @param {string} value
     */
    setValue(value) {
        return this.editor?.setData(value);
    }

    /**
     * Creates the editor.
     * @return {Promise<unknown>}
     */
    createEditor() {
        return ClassicEditor.create(this.node)
            .then((editor) => {
                // editor.isReadOnly = this.state.readOnly;
                if (this.state.readOnly) {
                    editor.enableReadOnlyMode(GENERIC_EDITOR_LOCK);
                }
                else {
                    editor.disableReadOnlyMode(GENERIC_EDITOR_LOCK);
                }
                editor.model.document.on('change:data', (e) => {
                    const event = new CustomEvent('change', e)
                    this.node.dispatchEvent(event);
                })
                this.editor = editor;
                return editor;
            });
    }

    /**
     * Renders state.
     * Use this to persist (read only) state to DOM
     * @param {Object} state Read only state.
     */
    render({readOnly}) {
        if (!this.editor) {
            this.editor = this.createEditor();
            return;
        }
        //this.editor.isReadOnly = readOnly;
        if (readOnly) {
            this.editor.enableReadOnlyMode(GENERIC_EDITOR_LOCK);
        }
        else {
            this.editor.disableReadOnlyMode(GENERIC_EDITOR_LOCK);
        }
    }
}

// Start
export const availableEditors = [...MARKDOWN_EDITORS].map((node) => new MarkdownEditor(node)).reduce((acc, val) => {
    return {...acc, [val.node.id]: val};
}, {})
