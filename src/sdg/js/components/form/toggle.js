import {FormComponent} from './abstract/form_component';


/**
 * @type {NodeListOf<HTMLElement>}
 * TODO: All toggles within a form a considered to control editable for now.
 **/
const FORM_TOGGLES = document.querySelectorAll('.form .toggle');


/**
 * Contains logic for a form to contain a toggle which controls whether fields should be editable.
 * Can be applied to all forms, only has effect when toggle is found (by id).
 */
class FormToggle extends FormComponent {
    /**
     * Constructor method.
     * @param {HTMLElement} node
     * @param {Object} initialState
     */
    constructor(node, initialState = {}) {
        super(node, initialState);
        this.node = this.node.querySelector('input');
    };

    /**
     * Binds events to callbacks.
     * Use this to define EventListeners, MutationObservers etc.
     */
    bindEvents() {
        this.node.addEventListener('change', (e) => this.setState({
            editable: e.target.checked,
        }));
    }

    /**
     * Returns an HTMLElement representing the scope of the toggle.
     * For an "edit all" toggle the form is considered to be the scope, for an "edit control" toggle the form control is
     * considered to be the element scope.
     * @return {([HTMLElement]|[HTMLFormElement])}
     */
    getElementScope() {
        try {
            return [this.getFormControl()];
        } catch (e) {
            return this.node.form.querySelectorAll('.form__control');
        }
    }

    /**
     * Renders state.
     * Gets called when state gets updated.
     * Use this to persist (read only) state to DOM.
     * @param {Object} state Read only state.
     */
    render(state) {
        const {editable} = state;
        const elementScope = this.getElementScope();
        [...elementScope].forEach((formControl) => this.setFormControlDisabled(!editable, formControl));
    }
}

// Start!
[...FORM_TOGGLES].forEach((node) => new FormToggle(node));
