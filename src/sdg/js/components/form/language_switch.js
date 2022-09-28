import {FormComponent} from './abstract/form_component';

/** @type {NodeListOf<HTMLButtonElement>} */
const LANGUAGE_SWITCHES = document.querySelectorAll('.form__language-switch');

/**
 * Sets the language of the form control.
 */
export class LanguageSwitch extends FormComponent {
    /**
     * Binds events to callbacks.
     * Use this to define EventListeners, MutationObservers etc.
     */
    bindEvents() {
        super.bindEvents();

        if (this.isGlobal()) {
            this.node.parentElement.addEventListener('click', this.onButtonGroupClick.bind(this));
            return;
        }

        const formControl = this.getFormControl();

        [...formControl.querySelectorAll('input, textarea')].forEach((inputOrTextarea) => {
            inputOrTextarea.addEventListener('change', this.updateChanged.bind(this));
        });

        const observer = new MutationObserver(this.updateActive.bind(this));
        observer.observe(formControl, {attributes: true});
    }

    /**
     * Returns whether this language switch is global.
     */
    isGlobal() {
        return !this.getFormControl();  // Detect based on presence of form control, null means global.
    }

    /**
     * Returns the active form control.
     * @return {(HTMLElement|null)}
     */
    getFormControl() {
        const language = this.getLanguage();
        try {
            return this._getParent('form__language-wrapper').querySelector(`.form__control[lang=${language}]`);
        } catch (e) {
            return null;
        }
    }

    /**
     * Returns the icon.
     * @return {SVGSVGElement}
     */
    getIcon() {
        return this.node.querySelector('svg');
    }


    /**
     * Returns the language of this button.
     * @return {string}
     */
    getLanguage() {
        return this.node.lang;
    }

    /**
     * Gets called before the first render cycle.
     * Use this to sync state with DOM before first render.
     */
    beforeMount() {
        super.beforeMount();
        const active = this.node.classList.contains('button--active');
        let initialValue;

        try {
            initialValue = this.getValue();
        } catch (e) {
            initialValue = null;

        }
        this.setState({active, initialValue});
    }

    /**
     * Gets called when `this.node` is clicked.
     * @param {MouseEvent} event
     */
    onClick(event) {
        super.onClick(event);
        this.setActiveLanguage(this.getLanguage(), this.isGlobal());
    }

    /**
     * Gets called when a global language switch button group is clicked.
     * @param {MouseEvent} e
     */
    onButtonGroupClick(e) {
        const active = this.getLanguage() === e.target.lang;
        this.setState({active: active});
    }

    /**
     * Updates the active state based the active language.
     */
    updateActive() {
        const active = this.getActiveLanguage() === this.getLanguage();
        this.setState({active});
    }

    /**
     * Updates the changes state based on the reference.
     */
    updateChanged(e) {
        const changed = this.getValue() !== this.state.initialValue;
        this.setState({changed});
    }

    /**
     * Renders state.
     * Gets called when state gets updated.
     * Use this to persist (read only) state to DOM.
     * @param {Object} state Read only state.
     */
    render(state) {
        const {active, changed} = state;
        this.node.classList.toggle('button--active', Boolean(active));

        const icon = this.getIcon();
        if (!icon) return;

        icon.setAttribute('aria-hidden', true);
        if (changed) {
            icon.removeAttribute('aria-hidden');
        }
    }
}

// Start!
[...LANGUAGE_SWITCHES].forEach((node) => new LanguageSwitch(node));
