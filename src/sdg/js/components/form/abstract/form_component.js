import {Component} from '../../abstract/component';
import {availableEditors} from '../../markdown';


/**
 * Base class for implementing components within the update form.
 * @abstract
 */
export class FormComponent extends Component {
    /**
     * Binds events to callbacks.
     * Use this to define EventListeners, MutationObservers etc.
     */
    bindEvents() {
        this.node.addEventListener('click', this.onClick.bind(this));
    }

    /**
     * Gets called when this.node gets clicked.
     * @param {MouseEvent} event
     */
    onClick(event) {
    }

    /**
     * Returns the form control (table cell) containing this button.
     * @param {HTMLElement} [child]
     * @return {HTMLElement}
     */
    getFormControl(child) {
        return this._getParent('form__cell', child);
    }

    /**
     * Returns whether the form control is disabled.
     * @return {boolean}
     */
    getFormControlDisabled() {
        return this.getFormControl().classList.contains('form__cell--disabled');
    }

    /**
     * Sets the disabled state of the form control.
     * @param {boolean} disabled
     * @param {HTMLElement} [formControl]
     */
    setFormControlDisabled(disabled, formControl = this.getFormControl()) {
        formControl.classList.toggle('form__cell--disabled', disabled);
        const toggleInput = formControl.querySelector('.toolbar .toggle input ');

        // Update toggle.
        if(toggleInput) {
            toggleInput.checked = !disabled;
        }

        // Update input/select/textarea.
        [...formControl.querySelectorAll(`
            .form__cell input,
            .form__cell select,
            .form__cell textarea
        `)].forEach((field) => {
            field.readOnly = disabled;
        });

        // Update reference button.
        formControl.querySelector('.form__cell .form__reference-btn')?.toggleAttribute('disabled', disabled);
    }

    /**
     * Returns the container for the field.
     * @return {HTMLElement}
     */
    getFieldContainer() {
        return this.getFormControl().querySelector('.tabs__table-cell--field');
    }

    /**
     * Returns either the input or textarea for this diff button.
     * @return {(HTMLInputElement|HTMLTextAreaElement)}
     */
    getInputOrTextarea() {
        return this.getFormControl().querySelector('input, textarea');
    }

    /**
     * Returns a single HTMLElement containig all visible fields for the input or textarea.
     */
    getVisibleInputOrTextarea() {
        const fieldContainer = this.getFieldContainer();
        return fieldContainer.querySelector('input, .markdownx');
    }

    /**
     * Returns the table.
     * @param {HTMLTableElement} [child]
     * @return {HTMLTableElement}
     */
    getTable(child) {
        return this._getParent('tabs__table', child);
    }

    /**
     * Returns the HTMLElement containing the version labels.
     * @return {HTMLElement}
     */
    getVersionsContainer() {
        return this.getFormControl().querySelector('.tabs__table-cell--versions');
    }

    /**
     * Returns the value of either the input or textarea.
     * @return {string}
     */
    getValue() {
        const inputOrTextarea = this.getInputOrTextarea();
        return availableEditors[inputOrTextarea.id]?.getValue() || inputOrTextarea.value;
    }

    /**
     * Sets the value of either the input or textarea.
     * @param {string} value
     */
    setValue(value) {
        const inputOrTextarea = this.getInputOrTextarea();
        const editor = availableEditors[inputOrTextarea.id];

        if (editor) {
            editor.setValue(value);
            return;
        }

        inputOrTextarea.value = value;
    }

    /**
     * Returns a parent based on className.
     * @param {string} className An item in the parents classList.
     * @param {HTMLElement} [child=this.node]
     * @return {HTMLElement}
     * @private
     */
    _getParent(className, child = this.node) {
        let iteratedNode = child.parentElement;
        let i = 1;

        while (!iteratedNode || !iteratedNode.classList.contains(className)) {
            iteratedNode = iteratedNode.parentElement;
            i++;

            if (!iteratedNode || i > 10) {
                throw new Error(`Maximum recursion depth exceeded while localizing form control for ${child}.`);
            }
        }

        return iteratedNode;
    }
}
