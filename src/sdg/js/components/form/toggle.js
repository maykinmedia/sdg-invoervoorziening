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
     * @return {(HTMLElement|HTMLFormElement)}
     */
    getElementScope() {
        try {
            return this.getFormControl();
        } catch (e) {
            return this.node.form;
        }
    }

    /**
     * Renders state.
     * Gets called when state gets updated.
     * Use this to persist (read only) state to DOM.
     * @param {Object} state Read only state.
     */
    render({editable}) {
        const elementScope = this.getElementScope();

        // Update the current element.
        this.node.checked = editable;

        // Update synced elements.
        try {
            this.getFormControl();  // Use as indicator whether toggle is bound to form control, raises error if not.
        } catch (e) {
            [...this.node.form.querySelectorAll('.toggle input')].forEach((toggle) => toggle.checked = editable);
        }

        // Set readonly.
        [...elementScope.querySelectorAll(`
            .form__cell input,
            .form__cell select,
            .form__cell textarea
        `)].forEach((field) => {
            const formControl = this.getFormControl(field);
            formControl.classList.toggle('form__cell--disabled', !editable);
            field.readOnly = !editable;
        });

        // Set disabled.
        [...elementScope.querySelectorAll(
            'button'
        )].forEach((button) => button.disabled = !editable);

    }
}

// Start!
[...FORM_TOGGLES].forEach((node) => new FormToggle(node));
