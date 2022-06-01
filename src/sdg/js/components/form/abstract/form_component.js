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
     * @param {string} [language]
     * @return {HTMLElement}
     */
    getFormControl(child = undefined) {
        return this._getParent('form__control', child);
    }

    /**
     * Returns whether the form control is disabled.
     * @return {boolean}
     */
    getFormControlDisabled() {
        return this.getFormControl().classList.contains('form__control--disabled');
    }

    /**
     * Sets the disabled state of the form control.
     * @param {boolean} disabled
     * @param {HTMLElement} [formControl]
     */
    setFormControlDisabled(disabled, formControl = this.getFormControl()) {
        formControl.classList.toggle('form__control--disabled', disabled);
        const toggleInput = formControl.querySelector('.toolbar .toggle input ');

        // Update toggle.
        if (toggleInput) {
            toggleInput.checked = !disabled;
        }

        // Update input/select/textarea.
        [...formControl.querySelectorAll(`
            .form__control input,
            .form__control select,
            .form__control textarea
        `)].forEach((field) => {
            field.readOnly = disabled;
        });

        // Update reference button.
        formControl.querySelector('.form__control .form__reference-btn')?.toggleAttribute('disabled', disabled);
    }

    /**
     * Returns the container for the field.
     * @return {HTMLElement}
     */
    getFieldContainer() {
        return this.getFormControl().querySelector(`.form__control-body`);
    }

    /**
     * Returns either the input or textarea for this diff button.
     * @return {(HTMLInputElement|HTMLTextAreaElement)}
     */
    getInputOrTextarea() {
        return this.getFieldContainer().querySelector('input, textarea');
    }

    /**
     * Returns a single HTMLElement containig all visible fields for the input or textarea.
     */
    getVisibleInputOrTextarea() {
        const fieldContainer = this.getFieldContainer();
        return fieldContainer.querySelector('input, .markdownx').parentElement;
    }

    /**
     * Returns all the language wrappers.
     * @return {HTMLElement}
     */
    getLanguageWrappers() {
        return this._getParent('form').querySelectorAll('.form__language-wrapper');
    }

    /**
     * Returns the language wrapper for child.
     * @param [child]
     * @return {HTMLElement}
     */
    getLanguageWrapper(child) {
        return this._getParent('form__language-wrapper', child);
    }

    /**
     * Returns the language of the field container containing `this.node`.
     * @return {string}
     */
    getLanguage() {
        return this.getFieldContainer().lang;
    }

    /**
     * Returns the active language.
     * @return {string}
     */
    getActiveLanguage() {
        return this.getLanguageWrapper().lang;
    }

    /**
     * Set the languages.
     * @param {string} language
     * @param {boolean} [global=false] Whether to set all form controls to language.
     */
    setActiveLanguage(language, global = false) {
        const languageWrappers = (global) ? this.getLanguageWrappers() : [this.getLanguageWrapper()];

        [...languageWrappers].forEach((languageWrapper) => {
            languageWrapper.lang = language;

            [...languageWrapper.querySelectorAll('.form__control')].forEach((formControl) => {
                if (formControl.lang === language) {
                    formControl.removeAttribute('aria-hidden');
                } else {
                    formControl.setAttribute('aria-hidden', true);
                }
            });
        })
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
        return availableEditors[inputOrTextarea.id]?.getValue() || inputOrTextarea.value
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

            if (!iteratedNode || i > 100) {
                throw new Error(`Maximum recursion depth exceeded while localizing parent with className ${className} for ${child}.`);
            }
        }

        return iteratedNode;
    }
}
