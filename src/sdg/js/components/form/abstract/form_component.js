import { Component } from "../../abstract/component";
import { availableEditors } from "../../markdown";

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
        this.node.addEventListener("click", this.onClick.bind(this));
    }

    /**
     * Gets called when this.node gets clicked.
     * @param {MouseEvent} event
     */
    onClick(event) {}

    /**
     * Returns the form.
     * @param {HTMLElement} child
     * @returns {HTMLElement}
     */
    getForm(child = undefined) {
        return this._getParent("form", child);
    }

    /**
     * Returns the form field containing multiple fields.
     * @param {HTMLElement} child
     * @returns {HTMLElement}
     */
    getFormField(child = undefined) {
        return this._getParent("form__field", child);
    }

    /**
     * Return the current reference form.
     * @param {String} language
     * @return {HTMLTemplateElement}
     */
    getCurrentReferenceForm(language) {
        return document.querySelector(`.form__reference-${language}`);
    }

    /**
     * Returen the previous reference form.
     * @return {HTMLTemplateElement}
     */
    getPreviousReferenceForm(language) {
        return document.querySelector(`.form__previousreference-${language}`);
    }

    /**
     * Returns the reference toolbar.
     * @param {HTMLElement} child
     * @return {HTMLElement}
     */
    getReferenceTextToolbar(child = undefined) {
        return this.getFormField(child).querySelector(".form__field-toolbar");
    }

    /**
     * Returns the language of the control - works only from a nested element inside `.form__control`
     * @param {HTMLElement} child
     * @returns {string} language string defined on the '.form__control' element - eg. 'nl'
     */
    getControlLanguage(child = undefined) {
        return this._getParent("form__control", child).lang;
    }

    /**
     * Returns an object containing a property for each different `.reference` and it's language.
     * @param {HTMLElement} child
     * @returns {{ [language: string]: HTMLElement }}
     */
    getReferenceElements(child = undefined) {
        const nodes = this.getFormField(child).querySelectorAll(".reference");
        return this._localizedGetter(nodes);
    }

    /**
     * Returns an object containing a property for each different `.reference__preview` and it's language.
     * @param {HTMLElement} child
     * @returns {{ [language: string]: HTMLElement }}
     */
    getReferencePreviewElements(child = undefined) {
        const nodes = this.getFormField(child).querySelectorAll(
            ".reference__preview"
        );
        return this._localizedGetter(nodes);
    }

    /**
     * Returns an object containing a property for each different `.reference__versions` and it's language.
     * @param {HTMLElement} child
     * @returns {{ [language: string]: HTMLElement }}
     */
    getReferenceVersionElements(child = undefined) {
        const nodes = this.getFormField(child).querySelectorAll(
            ".reference__versions"
        );
        return this._localizedGetter(nodes);
    }

    /**
     * Returns an object containing a property for each different `.diff` and it's language.
     * @param {HTMLElement} child
     * @returns {{ [language: string]: HTMLElement }}
     */
    getDiffElements(child = undefined) {
        const nodes = this.getFormField(child).querySelectorAll(".diff");
        return this._localizedGetter(nodes);
    }

    /**
     * Returns an object containing a property for each different `.diff__preview` and it's language.
     * @param {HTMLElement} child
     * @returns {{ [language: string]: HTMLElement }}
     */
    getDiffPreviewElements(child = undefined) {
        const nodes =
            this.getFormField(child).querySelectorAll(".diff__preview");
        return this._localizedGetter(nodes);
    }

    /**
     * Returns an object containing a property for each different `.diff__versions` and it's language.
     * @param {HTMLElement} child
     * @returns {{ [language: string]: HTMLElement }}
     */
    getDiffVersionElements(child = undefined) {
        const nodes =
            this.getFormField(child).querySelectorAll(".diff__versions");
        return this._localizedGetter(nodes);
    }

    /**
     * Returns an object containing a property for each different `input, textarea` and it's language.
     * @param {HTMLElement} child
     * @returns {{ [language: string]: HTMLElement }}
     */
    getInputOrTextareas(child = undefined) {
        const nodes =
            this.getFormField(child).querySelectorAll("input, textarea");
        return this._localizedGetter(nodes);
    }

    /**
     * Returns an object containing all visible fields as value with the key as the language.
     * @returns {{ [language: string]: HTMLElement} }
     */
    getVisibleInputOrTextareas(child = undefined) {
        const nodes =
            this.getFormField(child).querySelectorAll("input, .markdownx");
        return this._localizedGetter(nodes, "parentElement");
    }

    /**
     * Returns the values of either the inputs or textareas.
     * @returns {{ [language: string]: string} }
     */
    getValues() {
        return Object.entries(this.getInputOrTextareas()).reduce(
            (acc, [language, node]) => {
                const value = availableEditors[node.id]?.getValue();
                if (value) acc[language] = value;
                else if (value == "") acc[language] = value;
                else acc[language] = node.value;
                return acc;
            },
            {}
        );
    }

    /**
     * Sets the value of either the input or textarea.
     * @param {string} id
     * @param {string} value
     */
    setValue(id, value) {
        const editor = availableEditors[id];
        const inputOrTextareas = this.getInputOrTextareas();

        if (editor) {
            editor.setValue(value);
            return;
        }

        Object.values(inputOrTextareas).forEach((node) => {
            if (node.id == id) node.value = value;
        });
    }

    /**
     * Format the nodes in an object that has the key as language and the element als value.
     * @param {NodeListOf<HTMLElement>} nodes
     * @param {string} nodeProperty a property of node that can be returned
     * @returns {{ [language: string]: HTMLElement} }
     * @private
     */
    _localizedGetter(nodes, nodeProperty = undefined) {
        return Array.from(nodes).reduce((acc, node) => {
            const language = node.lang
                ? node.lang
                : this.getControlLanguage(node);

            // return the property of a node under the key of the language.
            if (nodeProperty) acc[language] = node[nodeProperty];
            else acc[language] = node;
            return acc;
        }, {});
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
                throw new Error(
                    `Maximum recursion depth exceeded while localizing parent with className ${className} for ${child}.`
                );
            }
        }

        return iteratedNode;
    }
}
