import {ReferenceTextComponent} from './abstract/reference_text_component';


/** @type {NodeListOf<HTMLAnchorElement>} */
const USE_REFERENCE_BUTTONS = document.querySelectorAll('.form__reference-btn');


/**
 * Button allow the user to use the reference text.
 */
class UseReferenceButton extends ReferenceTextComponent {
    /**
     * Gets called when this.node gets clicked.
     * @param {MouseEvent} event
     */
    onClick(event) {
        event.preventDefault();
        this.setValue(this.getPreviousVersionData().input.value);
    }

    /**
     * Updates the label state based on disabled attribute.
     */
    updateLabel() {
        super.updateLabel();

        if(this.getFormControlDisabled()) {
            this.setState({label: 'Aanpassen uitgeschakeld'});
        } else {
            this.setState({label: this.state.originalLabel});
        }
    }
}

// Start!
[...USE_REFERENCE_BUTTONS].forEach((node) => new UseReferenceButton(node));
