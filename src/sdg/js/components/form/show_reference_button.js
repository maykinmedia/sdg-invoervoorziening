import { ReferenceTextComponent } from "./abstract/reference_text_component";
import { hideElement, showElement } from "./utils";

/** @type {NodeListOf<HTMLAnchorElement>} */
const SHOW_REFERENCE_BUTTONS = document.querySelectorAll(".form__display-btn");

/**
 * Button allow the user to use the reference text.
 */
class ShowReferenceButton extends ReferenceTextComponent {
    /**
     * Gets called when this.node gets clicked.
     * @param {MouseEvent} event
     */
    onClick(event) {
        event.preventDefault();
        this.setState({
            active: !this.state.active,
            referenceHTML: this.getCurrentReferenceHTML(),
        });
    }

    /**
     * Shows the reference text.
     */
    showReferenceText() {
        showElement(this.getReferenceTextToolbar());
        Object.values(this.getReferenceElements()).forEach(showElement);
    }

    /**
     * Hide the refence text.
     */
    hideReferenceText() {
        hideElement(this.getReferenceTextToolbar());
        Object.values(this.getReferenceElements()).forEach(hideElement);
    }

    /**
     * Renders state.
     * Gets called when state gets updated.
     * Use this to persist (read only) state to DOM.
     * @param {Object} state Read only state.
     */
    render(state) {
        super.render(state);
        const { active } = state;

        this.createCurrentReferences();
        if (active) {
            this.showReferenceText();
        } else {
            this.hideReferenceText();
        }
    }
}

// Start!
[...SHOW_REFERENCE_BUTTONS].forEach((node) => new ShowReferenceButton(node));
