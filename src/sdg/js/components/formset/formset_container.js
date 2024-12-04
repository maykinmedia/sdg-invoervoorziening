import { FormsetFormComponent } from "./abstract/formset_form_component";

const FORMSET = document.querySelectorAll(".formset");

export class OrderContainer extends FormsetFormComponent {
    /**
     * Gets called after the first render cycle.
     * Use this to sync state with DOM after first render.
     */
    onMount() {
        super.onMount();
        this.renderForm();
    }

    /**
     * Render the form and the correct meta data
     */
    renderForm() {
        this.renderOrder();
        this.renderOrderFieldButtonDisabled();

        this.setFormMetadata();
    }

    renderOrder() {
        // Set the correct order, new forms have automatically the correct order.
        this.getSubformOrderInfo().forEach(
            ({ orderText, orderField, counter, counter0 }) => {
                // Render orderText
                if (orderText.textContent !== counter)
                    orderText.textContent = counter;

                // Update the order field
                if (orderField && orderField.value !== counter0)
                    orderField.setValue(counter0);
            }
        );
    }

    /**
     * Render the disabled state of the order field buttons.
     */
    renderOrderFieldButtonDisabled() {
        this.getSubformOrderElementInfo().forEach(
            ({ isFirst, isLast, incElement, decElement }) => {
                if (!incElement && !decElement) return;
                isFirst
                    ? decElement.setAttribute("disabled", true)
                    : decElement.removeAttribute("disabled");
                isLast
                    ? incElement.setAttribute("disabled", true)
                    : incElement.removeAttribute("disabled");
            }
        );
    }

    /**
     * Set the form metadata.
     * - Total forms.
     */
    setFormMetadata() {
        // Update the total forms field.
        this.getFormsetTotalFormsField().setValue(this.getTotalFormsCount());
    }

    render(state) {
        super.render(state);
        this.renderForm();
    }
}

// Start!
[...FORMSET].forEach((node) => new OrderContainer(node));
