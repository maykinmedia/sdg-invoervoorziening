import {ReferenceTextComponent} from './abstract/reference_text_component';


/** @type {NodeListOf<HTMLAnchorElement>} */
const SHOW_REFERENCE_BUTTONS = document.querySelectorAll('.form__display-btn');


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
        this.setState({active: !this.state.active, referenceHTML: this.getReferenceHTML()});
    }

    /**
     * Returns the icon.
     * @return {SVGSVGElement}
     */
    getIcon() {
        return this.node.querySelector('svg');
    }

    /**
     * Shows the reference text.
     */
    showReferenceText() {
        this.getReferenceTextContainer().removeAttribute('aria-hidden');
        this.getReferenceTextToolbar().removeAttribute('aria-hidden');
    }

    /**
     * Hide the refence text.
     */
    hideReferenceText() {
        this.getReferenceTextContainer().setAttribute('aria-hidden', true);
        this.getReferenceTextToolbar().setAttribute('aria-hidden', true);
    }

    /**
     * Renders state.
     * Gets called when state gets updated.
     * Use this to persist (read only) state to DOM.
     * @param {Object} state Read only state.
     */
    render(state) {
        super.render(state);

        const {active, referenceHTML} = state;
        const iconRotation = (active) ? 90 : 0;

        this.getIcon().style.transform = `rotate(${iconRotation}deg)`;

        if (active) {
            this.getReferenceTextContainer().innerHTML = referenceHTML;
            this.showReferenceText();
        } else {
            this.hideReferenceText();
        }
    }
}

// Start!
[...SHOW_REFERENCE_BUTTONS].forEach((node) => new ShowReferenceButton(node));
