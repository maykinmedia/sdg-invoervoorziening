import {Component} from '../../abstract/component';
import {availableEditors} from '../../markdown';


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
     * Returns the reference text template.
     * @return {HTMLTemplateElement}
     */
    getReferenceTemplate() {
        return document.querySelector(".form__reference--display-template");
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
     * Returen the reference form.
     * @return {HTMLTemplateElement}
     */
    getCurrentReferenceForm() {
        const referenceFormSelector = this.getTable().dataset.reference;
        return document.querySelector(referenceFormSelector);
    }

    /**
     * Returen the previous reference form.
     * @return {HTMLTemplateElement}
     */
    getPreviousReferenceForm() {
        const previousReferenceFormSelector = this.getTable().dataset.previousreference;
        return document.querySelector(previousReferenceFormSelector);
    }

    /**
     * Returns the HTMLElement containing the version labels.
     * @return {HTMLElement}
     */
    getVersionsContainer() {
        return this.getFormControl().querySelector('.tabs__table-cell--versions');
    }

    /**
     * Returns the current version data.
     * @return {{input: (HTMLInputElement|HTMLTextAreaElement), title: string}}
     */
    getCurrentVersionData() {
        const inputOrTextarea = this.getInputOrTextarea();
        const currentReferenceForm = this.getCurrentReferenceForm();
        const currentReferenceInput = currentReferenceForm.content.querySelector(`#${inputOrTextarea.id}`);

        return {
            'title': 'Uw tekst',
            'input': currentReferenceInput,
        };
    }

    /**
     * Returns the previous version data.
     * @return {{input: (HTMLInputElement|HTMLTextAreaElement), title: string}}
     */
    getPreviousVersionData() {
        const inputOrTextarea = this.getInputOrTextarea();
        const previousReferenceForm = this.getPreviousReferenceForm();
        const previousReferenceInput = previousReferenceForm.content.querySelector(`#${inputOrTextarea.id}`);

        return {
            'title': previousReferenceForm.dataset.title,
            'input': previousReferenceInput,
        };
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

        if(editor) {
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
    _getParent(className, child=this.node) {
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
