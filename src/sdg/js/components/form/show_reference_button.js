import showdown from 'showdown';
import {FormComponent} from './abstract/form_component';


/** @type {NodeListOf<HTMLAnchorElement>} */
const SHOW_REFERENCE_BUTTONS = document.querySelectorAll('.form__display-btn');


/**
 * Button allow the user to use the reference text.
 */
class ShowReferenceButton extends FormComponent {
    /**
     * Gets called when this.node gets clicked.
     * @param {MouseEvent} event
     */
    onClick(event) {
        event.preventDefault();
        const inputOrTextarea = this.getInputOrTextarea();
        const referenceForm = this.getCurrentReferenceForm();
        const referenceField = referenceForm.content.getElementById(inputOrTextarea.id);
        const referenceHTML = new showdown.Converter().makeHtml(referenceField.value);

        this.setState({active: !this.state.active, referenceHTML: referenceHTML});
    }

    /**
     * Returns the icon.
     * @return {SVGSVGElement}
     */
    getIcon() {
        return this.node.querySelector('svg');
    }

    /**
     * Sets the active icon.
     */
    setActiveIcon() {
        const icon = this.getIcon();
        icon.classList.remove('fa-chevron-right');
        icon.classList.add('fa-chevron-down');
    }

    /**
     * Sets the inactive icon.
     */
    setInActiveIcon() {
        const icon = this.getIcon();
        icon.classList.remove('fa-chevron-down');
        icon.classList.add('fa-chevron-right');
    }

    /**
     * Shows the reference text.
     */
    showReferenceText() {
        if (!this.referenceTextContainer) {
            return;
        }
        this.referenceTextContainer.style.removeProperty('display');
    }

    /**
     * Hide the refence text.
     */
    hideReferenceText() {
        if (!this.referenceTextContainer) {
            return;
        }
        this.referenceTextContainer.style.setProperty('display', 'none');
    }

    /**
     * Renders state.
     * Gets called when state gets updated.
     * Use this to persist (read only) state to DOM.
     * @param {Object} state Read only state.
     */
    render({active, referenceHTML}) {
        this.node.classList.toggle('button--active', Boolean(active));

        if (!this.referenceTextContainer) {
            const referenceTemplate = this.getReferenceTemplate();
            this.referenceTextContainer = document.importNode(referenceTemplate.content.children[0], true);
            this.getFormControl().appendChild(this.referenceTextContainer);
        }

        const referenceHTMLWrapper = this.referenceTextContainer.querySelector('.reference__display--content');
        referenceHTMLWrapper.innerHTML = referenceHTML;

        if (active) {
            this.setActiveIcon();
            this.showReferenceText();
        } else {
            this.setInActiveIcon();
            this.hideReferenceText();
        }
    }
}

// Start!
[...SHOW_REFERENCE_BUTTONS].forEach((node) => new ShowReferenceButton(node));
