import { FormsetFormComponent } from "./abstract/formset_form_component";

const INCREMENT_ELEMENTS = document.querySelectorAll(".order_increment");

export class IncrementOrder extends FormsetFormComponent {
    /**
     * Gets called when this.node gets clicked.
     * @param {MouseEvent} event
     */
    onClick(event) {
        event.preventDefault();
        event.stopPropagation();
        this.swapDown();
    }

    /**
     * Swap the current and next element in the DOM.
     * All the states should be controlled in the formset_container render function.
     */
    swapDown() {
        const currentElement = this.getFormsetForm(this.node);
        const nextElement = this.getNextVisibleElement(currentElement);

        if (nextElement) {
            return nextElement.after(currentElement);
        }
    }
}

[...INCREMENT_ELEMENTS].forEach((node) => new IncrementOrder(node));
