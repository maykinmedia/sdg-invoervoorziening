import { FormsetFormComponent } from "./abstract/formset_form_component";

const DECREMENT_ELEMENTS = document.querySelectorAll(".order_decrement");

export class DecrementOrder extends FormsetFormComponent {
    /**
     * Gets called when this.node gets clicked.
     * @param {MouseEvent} event
     */
    onClick(event) {
        event.preventDefault();
        event.stopPropagation();
        this.swapUp();
    }

    /**
     * Swap the previous and current element in the DOM.
     * All the states should be controlled in the formset_container render function.
     */
    swapUp() {
        const currentElement = this.getFormsetForm(this.node);
        const previousElement = this.getPreviousVisibleElement(currentElement);
        const parent = currentElement.parentElement;

        if (previousElement) {
            parent.insertBefore(currentElement, previousElement);
        }
    }
}

[...DECREMENT_ELEMENTS].forEach((node) => new DecrementOrder(node));
