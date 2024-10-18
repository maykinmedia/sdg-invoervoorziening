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

        Object.entries(this.getCurrentVersionData()).forEach(
            ([language, { input }]) => {
                if (language == this.getControlLanguage() && input.value)
                    this.setValue(input.id, input.value);
            }
        );
    }

    /**
     * Updates the disabled state based on whether reference HTML is available.
     */
    updateDisabled() {
        const referenceHTML = this.getCurrentReferenceHTML();

        if (!referenceHTML || !referenceHTML[this.getControlLanguage()]) {
            this.setState({ disabled: true });
        }
    }

    /**
     * Updates the label state based on disabled attribute.
     */
    updateLabel() {
        // Make sure we keep track of the original label.
        if (!this.state.originalLabel) {
            this.setState({ originalLabel: this.node.textContent });
        }

        const referenceHTML = this.getCurrentReferenceHTML();
        // Show custom label if no reference text is available.
        if (!referenceHTML || !referenceHTML[this.getControlLanguage()]) {
            this.setState({ label: "Geen standaardtekst beschikbaar" });
        } else if (this.state.originalLabel) {
            this.setState({ label: this.state.originalLabel });
        }
    }
}

// Start!
[...USE_REFERENCE_BUTTONS].forEach((node) => new UseReferenceButton(node));
