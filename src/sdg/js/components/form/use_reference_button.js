import {FormComponent} from './abstract/form_component';


/** @type {NodeListOf<HTMLAnchorElement>} */
const USE_REFERENCE_BUTTONS = document.querySelectorAll('.form__reference-btn');


/**
 * Button allow the user to use the reference text.
 */
class UseReferenceButton extends FormComponent {
    /**
     * Gets called when this.node gets clicked.
     * @param {MouseEvent} event
     */
    onClick(event) {
        event.preventDefault();
        this.setValue(this.getPreviousVersionData().input.value);
    }
}

// Start!
[...USE_REFERENCE_BUTTONS].forEach((node) => new UseReferenceButton(node));
