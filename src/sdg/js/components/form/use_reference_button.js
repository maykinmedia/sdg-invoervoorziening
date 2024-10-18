import { ReferenceTextComponent } from "./abstract/reference_text_component";

/** @type {NodeListOf<HTMLAnchorElement>} */
const USE_REFERENCE_BUTTONS = document.querySelectorAll(".form__reference-btn");

/**
 * Button allow the user to take over the reference text in all localized fields at the same time.
 */
class UseReferenceButton extends ReferenceTextComponent {
    /**
     * Gets called when this.node gets clicked.
     * @param {MouseEvent} event
     */
    onClick(event) {
        event.preventDefault();

        Object.values(this.getCurrentVersionData()).forEach(({ input }) => {
            // Set the value on both inputs at the same time (if there is a value availible)
            if (input.value) this.setValue(input.id, input.value);
        });
    }
}

// Start!
[...USE_REFERENCE_BUTTONS].forEach((node) => new UseReferenceButton(node));
