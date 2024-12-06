import { Component } from "../../abstract/component";
import { CheckboxField, NumberField, TextField } from "./field_utils";

/**
 * Base class for implementing components within the formset form component.
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
     * Get the formset body element from the form.
     * @param {HTMLElement} [child]
     * @returns {HTMLElement}
     */
    getFormBody(child = undefined) {
        return this._getForm(child).querySelector(".formset__body");
    }

    /**
     * Get all `.formset__form:not(.hidden)` elements.
     * @param {HTMLElement} [child]
     * @returns {number}
     */
    getTotalFormsCount(child = undefined) {
        return this.getFormBody(child).querySelectorAll(".formset__form")
            .length;
    }

    /**
     * Get all (visible) `.formset__form:not(.hidden)` elements.
     * @param {HTMLElement} [child]
     * @returns {NodeListOf<HTMLElement>}
     */
    getVisibileFormsetForms(child = undefined) {
        return this.getFormBody(child).querySelectorAll(
            ".formset__form:not(.hidden)"
        );
    }

    /**
     * Get the formset body element from the form.
     * @param {HTMLElement} [child]
     * @returns {HTMLElement}
     */
    getFormsetForm(child = undefined) {
        return this._getParent("formset__form", child);
    }

    /**
     * Get the imported node of the template content.
     * @returns {globalThis.DocumentFragment}
     */
    getImportedTemplate() {
        const template = this._getTemplate();
        return document.importNode(template.content, true);
    }

    /**
     * Get the order field of a `.formset__form` form.
     * @param {HTMLElement} form element with the class `.formset__form`
     * @returns {NumberField | undefined}
     */
    getFormOrderField(form) {
        const field = form.querySelector(".order_field");
        if (!field) return undefined;
        return new NumberField(field);
    }

    /**
     * Get the field that stores the id of a `.formset__form` form.
     * @param {HTMLElement} form
     * @returns {NumberField | undefined}
     */
    getFormIdField(form) {
        const field = form.querySelector(`[name="${form.dataset.prefix}-id"]`);
        if (!field) return undefined;
        return new NumberField(field);
    }

    /**
     * Get the field that stores a inputable name.
     * @returns {TextField | undefined}
     */
    getFormNameField() {
        const field = this.node.querySelector('input[name$="naam"]');
        if (!field) return undefined;
        return new TextField(field);
    }

    /**
     * Get the field that stores a inputable name.
     * @returns {TextField | undefined}
     */
    getFormNotInListCheckox() {
        const field = this.node.querySelector(
            'input[name$="staat_niet_in_de_lijst"]'
        );
        if (!field) return undefined;
        return new CheckboxField(field);
    }

    /**
     * Get the field that stores if the form should be removed on submit of a `.formset__form` form.
     * @param {HTMLElement} form
     * @returns {CheckboxField | undefined}
     */
    getFormRemoveField(form) {
        const field = form.querySelector(
            `[name="${form.dataset.prefix}-DELETE"]`
        );
        if (!field) return undefined;
        return new CheckboxField(field);
    }

    /**
     * Get the field that keeps track of the total amount of forms.
     * @returns {NumberField | undefined}
     */
    getFormsetTotalFormsField() {
        const field = document.querySelector('[name="form-TOTAL_FORMS"]');
        if (!field) return undefined;
        return new NumberField(field);
    }

    getDynamicTitleComponent() {
        return this.node.querySelector(".dynamic_title");
    }

    getCurrentOrderText(form) {
        return form.querySelector(".formset__current-order");
    }

    /**
     * Get the next visible element (recursive).
     * @param {HTMLElement} currentElement
     * @returns {HTMLElement | undefined} The next element without the class `.hidden`.
     */
    getNextVisibleElement(currentElement) {
        const nextElement = currentElement.nextElementSibling;
        if (!nextElement) return undefined;

        if (nextElement.classList.contains("hidden"))
            return this.getNextVisibleElement(nextElement);

        return nextElement;
    }

    /**
     * Get the previous visible element (recursive).
     * @param {HTMLElement} currentElement
     * @returns {HTMLElement | undefined} The previous element without the class `.hidden`.
     */
    getPreviousVisibleElement(currentElement) {
        const previousElement = currentElement.previousElementSibling;
        if (!previousElement) return undefined;

        if (previousElement.classList.contains("hidden"))
            return this.getPreviousVisibleElement(previousElement);

        return previousElement;
    }

    /**
     * Get the lowest availible form prefix value
     * @returns {number} lowest unused form prefix value
     */
    getLowestAvailiblePrefix() {
        return Array.from(this.getVisibileFormsetForms(this.node))
            .map((form) =>
                parseInt(form.dataset.prefix.replace("form-", ""), 10)
            )
            .filter((num) => !isNaN(num))
            .sort((a, b) => a - b)
            .reduce((prev, cur) => {
                if (prev === cur) prev++;
                return prev;
            }, 0);
    }

    /**
     * Get an array containing data about the order.
     * @returns {Array<{
     *  orderField: NumberField | undefined,
     *  counter0: number,
     *  counter: number,
     *  orderText: HTMLElement,
     * }>}
     */
    getSubformOrderInfo() {
        const subforms = this.getVisibileFormsetForms(this.node);

        return Array.from(subforms).map((form, index) => ({
            orderField: this.getFormOrderField(form),
            counter0: index,
            counter: index + 1,
            orderText: form.querySelector(".formset__current-order"),
        }));
    }

    /**
     * Get an array containing data about order and the order elements.
     * @returns {Array<{
     *  isFirst: boolean,
     *  isLast: boolean,
     *  incElement: HTMLElement,
     *  decElement: HTMLElement,
     * }>}
     */
    getSubformOrderElementInfo() {
        const subforms = this.getVisibileFormsetForms(this.node);

        return Array.from(subforms).map((cur, index) => ({
            isFirst: index == 0,
            isLast: index == subforms.length - 1,
            incElement: cur.querySelector(".order_increment"),
            decElement: cur.querySelector(".order_decrement"),
        }));
    }

    /**
     * Get the form element from the current `scope`
     * @param {HTMLElement} [child]
     * @returns {HTMLElement}
     * @private
     */
    _getForm(child = undefined) {
        return this._getParent("form", child);
    }

    /**
     * Get the `.formset__template` element.
     * @returns {HTMLTemplateElement}
     * @private
     */
    _getTemplate() {
        return document.querySelector(".formset__template");
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

        if (child.classList.contains(className)) return child;

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
