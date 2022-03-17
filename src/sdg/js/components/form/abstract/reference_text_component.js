/**
 * Base class for implementing components within the update form.
 * @abstract
 */
import showdown from 'showdown';
import {FormComponent} from './form_component';

export class ReferenceTextComponent extends FormComponent {
    /**
     * Options object.
     * Use this to specify the options of the component.
     *
     * @type {Object}
     */
    static options = {
        observe: true,
    }

    /**
     * Binds events to callbacks.
     * Use this to define EventListeners, MutationObservers etc.
     */
    bindEvents() {
        super.bindEvents();
        this.getReferenceTextToolbar().querySelector('.form__reference-btn').addEventListener('click', () => this.setState({active: false}));
    }

    /**
     * Gets called after the first render cycle.
     * Use this to sync state with DOM on initial mount.
     */
    onMount() {
        super.onMount();

        this.updateDisabled();
        this.updateLabel();
    }

    /**
     * Gets called when MutationObservers detects a mutation.
     * Only when `options.observe` is set to `true`.
     * Use this to sync state with DOM updates.
     * @param {MutationRecord} mutationRecord
     */
    onMutation(mutationRecord) {
        super.onMutation(mutationRecord);

        const disabled = Boolean(mutationRecord.target[mutationRecord.attributeName]);
        this.setState({disabled: disabled});

        this.updateDisabled();
        this.updateLabel();
    }

    /**
     * Updates the disabled state based on whether reference HTML is available.
     */
    updateDisabled() {
        if (!this.getReferenceHTML()) {
            this.setState({disabled: true})
        }
    }

    /**
     * Updates the label state based on disabled attribute.
     */
    updateLabel() {
        // Make sure we keep track of the original label.
        if (!this.state.originalLabel) {
            this.setState({originalLabel: this.node.textContent});
        }

        // Show custom label if no reference text is available.
        if (!this.getReferenceHTML()) {
            this.setState({label: 'Geen standaardtekst beschikbaar'});
        } else if (this.state.originalLabel) {
            this.setState({label: this.state.originalLabel});
        }
    }

    /**
     * Returns the current version data.
     * @return {{input: (HTMLInputElement|HTMLTextAreaElement), title: string}}
     */
    getCurrentVersionData() {
        const inputOrTextarea = this.getInputOrTextarea();
        const currentReferenceForm = this.getCurrentReferenceForm();
        const currentReferenceInput = currentReferenceForm.content.querySelector(`#${inputOrTextarea.id}`);

        return {
            'title': 'Uw tekst',
            'input': currentReferenceInput,
        };
    }

    /**
     * Returns the previous version data.
     * @return {{input: (HTMLInputElement|HTMLTextAreaElement), title: string}}
     */
    getPreviousVersionData() {
        const inputOrTextarea = this.getInputOrTextarea();
        const previousReferenceForm = this.getPreviousReferenceForm();
        const previousReferenceInput = previousReferenceForm.content.querySelector(`#${inputOrTextarea.id}`);

        return {
            'title': previousReferenceForm.dataset.title,
            'input': previousReferenceInput,
        };
    }

    /**
     * Returen the reference form.
     * @return {HTMLTemplateElement}
     */
    getCurrentReferenceForm() {
        const referenceFormSelector = this.getTable().dataset.reference;
        return document.querySelector(referenceFormSelector);
    }

    /**
     * Returen the previous reference form.
     * @return {HTMLTemplateElement}
     */
    getPreviousReferenceForm() {
        const previousReferenceFormSelector = this.getTable().dataset.previousreference;
        return document.querySelector(previousReferenceFormSelector);
    }

    /**
     * Returns the reference container.
     * @return {HTMLElement}
     */
    getReferenceTextContainer() {
        return this.getFormControl().querySelector('.form__reference');
    }

    /**
     * Returns the reference text template.
     * @return {HTMLTemplateElement}
     */
    getReferenceTemplate() {
        return document.querySelector(".form__reference--display-template");
    }

    /**
     * Returns the reference toolbar.
     * @return {HTMLElement}
     */
    getReferenceTextToolbar() {
        return this.getFormControl().querySelector('.form__reference + .toolbar');
    }

    /**
     * Returns the reference HTML.
     * @return {string}
     */
    getReferenceHTML() {
        const inputOrTextarea = this.getInputOrTextarea();
        const referenceForm = this.getCurrentReferenceForm();
        const referenceField = referenceForm.content.getElementById(inputOrTextarea.id);
        return new showdown.Converter().makeHtml(referenceField.value);
    }

    /**
     * Renders state.
     * Gets called when state gets updated.
     * Use this to persist (read only) state to DOM.
     * @param {Object} state Read only state.
     */
    render(state) {
        const {active, disabled, label} = state;

        super.render(state);

        this.node.classList.toggle('button--active', Boolean(active));

        if (disabled === true) {
            this.node.setAttribute('disabled', true);
        } else if (disabled === false) {
            this.node.removeAttribute('disabled');
        }

        if (label) {
            this.node.innerHTML = `${this.node.children[0]?.outerHTML} ${label}`;
        }
    }
}
