import Choices, { Item } from "choices.js";
import { FormsetFormComponent } from "./abstract/formset_form_component";
import { CHOICES_CONFIG } from "../choices";
import { stripParensText } from "../abstract/utils";

const DYNAMIC_CHECKBOXES = document.querySelectorAll(
    ".formset__form:not(.formset__form--preview)"
);

const CHOICE_PLACEHOLDER_ID = 1;

export class DynamicCheckbox extends FormsetFormComponent {
    constructor(node) {
        super(node);

        if (node.closest("#bevoegde_organisaties_form")) {
            this.shouldMount = true;
        } else this.shouldMount = false;
    }
    /**
     * Gets called before the first render cycle.
     */
    onMount() {
        super.onMount();

        if (!this.shouldMount) return;

        // Create choices
        this.choices = new Choices(
            this.node.querySelector(".choices"),
            CHOICES_CONFIG
        );

        this.handleMount();
    }

    /**
     * Binds events to callbacks.
     * Use this to define EventListeners, MutationObservers etc.
     */
    bindEvents() {
        super.bindEvents();

        if (!this.shouldMount) return;

        this.getFormNotInListCheckox().node.addEventListener(
            "change",
            this.onChange.bind(this)
        );

        this.selectElement = this.choices.passedElement.element;

        if (this.selectElement)
            this.selectElement.addEventListener(
                "change",
                this.handleSelect.bind(this)
            );
    }

    /**
     * Gets called when the input event is fired.
     * @param {Event} event
     */
    onChange(event) {
        this.handleChange(event.target.checked);
    }

    handleMount() {
        const placeholderSelected = this.isPlaceholderSelected();
        if (placeholderSelected) {
            this.showDynamicTitle();
            this.getFormNameField().node.removeAttribute("disabled");
        } else {
            const strippedLabel = stripParensText(
                this.choices.getValue().label
            );
            this.setValue(strippedLabel);
            this.hideDynamicTitle();
            this.getFormNameField().node.setAttribute("disabled", true);
        }
    }

    /**
     * Gets called onMount and when the select value changes.
     */
    handleSelect() {
        const placeholderSelected = this.isPlaceholderSelected();
        if (placeholderSelected) {
            this.setValue("");
            this.showDynamicTitle();
            this.getFormNameField().node.removeAttribute("disabled");
        } else {
            const strippedLabel = stripParensText(
                this.choices.getValue().label
            );
            this.setValue(strippedLabel);
            this.hideDynamicTitle();
            this.getFormNameField().node.setAttribute("disabled", true);
        }
    }

    /**
     * Handler for the change event, executed by the checkbox.
     * @param {boolean} checked
     */
    handleChange(checked) {
        checked ? this.showDynamicTitle() : this.hideDynamicTitle();
    }

    /**
     * Hide the dynamic title and force the checkbox value.
     */
    hideDynamicTitle() {
        this.getDynamicTitleComponent().classList.add("animated--hidden");
        this.getFormNotInListCheckox().setChecked(false);
    }

    /**
     * Show the dynamic title and force the checkbox value.
     */
    showDynamicTitle() {
        this.getDynamicTitleComponent().classList.remove("animated--hidden");
        this.getFormNotInListCheckox().setChecked(true);
    }

    /**
     * Set the value for the dynamic title and the name field.
     * @param {string} value
     */
    setValue(value) {
        // this.changeDynamicTitle(value);
        this.getFormNameField().setValue(value);

        // Dispatch input event so that dynamic_title can listen to it using the default input function.
        const inputEvent = new CustomEvent("forced_input", {
            bubbles: true,
            detail: {
                forcedValue: value,
            },
        });
        this.getFormNameField().node.dispatchEvent(inputEvent);
    }

    /**
     * Return a boolean indicating if the current selected item has the choiceId of the placeholder.
     * @returns {boolean}
     */
    isPlaceholderSelected() {
        /** @type {Item} */
        const value = this.choices.getValue();
        return value.choiceId == CHOICE_PLACEHOLDER_ID;
    }
}

// Start!
[...DYNAMIC_CHECKBOXES].forEach((node) => new DynamicCheckbox(node));

// r. 159
