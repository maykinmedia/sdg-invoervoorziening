import { initializeDynamicWidget } from "../dynamic_array";
import { FormsetFormComponent } from "./abstract/formset_form_component";
import { RemoveFormsetForm } from "./remove_formset_form";
import { DecrementOrder } from "./decrement_order";
import { IncrementOrder } from "./increment_order";
import { createTooltips } from "../tooltip";
import { Toggle } from "../toggle";
import { DynamicTitle } from "../dynamic_title";
import { DynamicCheckbox } from "./dynamic_checkbox";

/** @type {HTMLDivElement} */
const ADD_FORM_ELEMENT = document.querySelector(".formset__button--add");
const PREFIX_PLACEHOLDER = "__prefix__";

class AddFormsetForm extends FormsetFormComponent {
    /**
     * Gets called when this.node gets clicked.
     * @param {MouseEvent} event
     */
    onClick(event) {
        event.preventDefault();

        // Create and append a new location form.
        this.createForm();
    }

    /**
     * Create a new `.formset__form` from the template and append this form.
     */
    createForm() {
        const importedTemplate = this.getImportedTemplate();
        this.appendForm(importedTemplate);
    }

    /**
     * Append the template fragment and initialize the form.
     * @param {globalThis.DocumentFragment} importedTemplate The imported template element
     */
    appendForm(importedTemplate) {
        // Append the form
        const formBody = this.getFormBody();
        formBody.appendChild(importedTemplate);

        // Get the appended form and initialize it.
        const createdForm = formBody.children[formBody.children.length - 1];
        this.initializeForm(createdForm);
    }

    /**
     * Initialize the new `.formset__form` and rebind the events.
     * @param {HTMLElement} createdForm Element of the created form
     */
    initializeForm(createdForm) {
        // Replace the content and rebind the events
        this.replaceContent(createdForm);
        this.rebindEvents(createdForm);
    }

    /**
     * Replace the content inside the appended form.
     * @param {HTMLElement} createdForm The appended form.
     */
    replaceContent(createdForm) {
        // Get the lowest unused prefix;
        const newPrefix = this.getLowestAvailiblePrefix();

        // Replace the prefix_placeholder in the form classses.
        createdForm.classList.forEach((cls) => {
            if (cls.includes(PREFIX_PLACEHOLDER)) {
                createdForm.classList.remove(cls);
                createdForm.classList.add(
                    cls.replace(PREFIX_PLACEHOLDER, newPrefix)
                );
            }
        });

        // Replace the prefix_placeholder in the rest of the html.
        createdForm.innerHTML = createdForm.innerHTML.replaceAll(
            PREFIX_PLACEHOLDER,
            newPrefix
        );

        // Change the order text next indicating the row.
        this.getCurrentOrderText(createdForm).textContent = newPrefix + 1;

        // Set the form prefix on the form element.
        createdForm.dataset.prefix = `form-${newPrefix}`;
    }

    /**
     * Custom bindEvents function to activate logic on the
     * Manually rebind all classes to the elements.
     * @param {HTMLElement} form
     */
    rebindEvents(form) {
        createTooltips();

        const toggle = form.querySelector(".bem-toggle");
        if (toggle) new Toggle(toggle);

        const dynamicTitle = form.querySelector(".dynamic_title");
        if (dynamicTitle) new DynamicTitle(dynamicTitle);

        const removeButton = form.querySelector(".formset__remove");
        if (removeButton) new RemoveFormsetForm(removeButton);

        const incrementElement = form.querySelector(".order_increment");
        if (incrementElement) new IncrementOrder(incrementElement);

        const decrementElement = form.querySelector(".order_decrement");
        if (decrementElement) new DecrementOrder(decrementElement);

        const dynamicArrays = form.querySelectorAll(".dynamic__container");
        if (dynamicArrays)
            dynamicArrays.forEach((node) => initializeDynamicWidget(node));

        if (form.closest("#bevoegde_organisaties_form")) {
            new DynamicCheckbox(form);
        }
    }
}

// Start!
if (ADD_FORM_ELEMENT) new AddFormsetForm(ADD_FORM_ELEMENT);
