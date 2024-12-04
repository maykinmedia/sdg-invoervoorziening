import { FormsetFormComponent } from "./abstract/formset_form_component";

const REMOVE_ELEMENTS = document.querySelectorAll(".formset__remove");

export class RemoveFormsetForm extends FormsetFormComponent {
    /**
     * Gets called when this.node gets clicked.
     * @param {MouseEvent} event
     */
    onClick(event) {
        event.preventDefault();
        this.removeForm();
    }

    /**
     * Remove or hide the formset form.
     */
    removeForm() {
        const form = this.getFormsetForm(this.node);
        const idField = this.getFormIdField(form);
        // Check if the form existed or not.
        if (idField && idField.value) {
            // Hide form and check the checkbox that removes the form
            form.classList.add("hidden");
            this.getFormRemoveField(form).setChecked(true);
        } else {
            // Remove the form if it was never saved.
            form.remove();
        }
    }
}

// Start
[...REMOVE_ELEMENTS].forEach((node) => new RemoveFormsetForm(node));
