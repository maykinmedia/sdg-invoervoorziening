/**
 * Base class for implementing components within the update form.
 * @abstract
 */
import showdown from "showdown";
import { FormComponent } from "./form_component";

export class ReferenceTextComponent extends FormComponent {
    /**
     * Options object.
     * Use this to specify the options of the component.
     *
     * @type {Object}
     */
    static options = {
        observe: true,
    };

    /**
     * Binds events to callbacks.
     * Use this to define EventListeners, MutationObservers etc.
     */
    bindEvents() {
        super.bindEvents();
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

        const disabled = Boolean(
            mutationRecord.target[mutationRecord.attributeName]
        );
        this.setState({ disabled: disabled });

        this.updateDisabled();
        this.updateLabel();
    }

    /**
     * Updates the disabled state based on whether reference HTML is available.
     */
    updateDisabled() {
        const referenceHTML = this.getCurrentReferenceHTML();

        if (
            !referenceHTML ||
            Object.values(referenceHTML).every((value) => !value)
        ) {
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
        if (!referenceHTML || Object.values(referenceHTML).every((v) => !v)) {
            this.setState({ label: "Geen standaardteksten beschikbaar" });
        } else if (this.state.originalLabel) {
            this.setState({ label: this.state.originalLabel });
        }
    }

    /**
     * Returns an array containing the current version data for each language
     * @return {{
     *      [language: string]: {
     *          input: HTMLElement,
     *          title: string
     *      }
     * }}
     */
    getCurrentVersionData() {
        return Object.entries(this.getInputOrTextareas()).reduce(
            (acc, [language, node]) => {
                const currentReferenceForm =
                    this.getCurrentReferenceForm(language);
                const referenceField =
                    currentReferenceForm.content.getElementById(node.id);
                acc[language] = {
                    input: referenceField,
                    title: currentReferenceForm.dataset.title,
                };

                return acc;
            },
            {}
        );
    }

    /**
     * Returns an array containing the previous version data for each language
     * @return {{
     *      [language: string]: {
     *          input: HTMLElement,
     *          title: string
     *      }
     * }}
     */
    getPreviousVersionData() {
        const inputOrTextareas = this.getInputOrTextareas();

        return Object.entries(inputOrTextareas).reduce(
            (acc, [language, node]) => {
                const previousFormReference =
                    this.getPreviousReferenceForm(language);
                const referenceField =
                    previousFormReference.content.getElementById(node.id);
                acc[language] = {
                    input: referenceField,
                    title: previousFormReference.dataset.title,
                };

                return acc;
            },
            {}
        );
    }

    /**
     * Returns the reference HTML.
     * @return {{[language: string]: any}}
     */
    getCurrentReferenceHTML() {
        return Object.entries(this.getCurrentVersionData()).reduce(
            (acc, [language, { input }]) => {
                acc[language] = new showdown.Converter({
                    tables: true,
                }).makeHtml(input.value);
                return acc;
            },
            {}
        );
    }

    /**
     * Create the references below each field
     * @param {{[language: string]: any}} referenceHTML
     */
    createCurrentReferences() {
        const referenceHTML = this.getCurrentReferenceHTML();

        Object.entries(this.getReferencePreviewElements()).forEach(
            ([language, node]) => {
                if (referenceHTML[language])
                    node.innerHTML = referenceHTML[language];
            }
        );
    }

    /**
     * Renders state.
     * Gets called when state gets updated.
     * Use this to persist (read only) state to DOM.
     * @param {Object} state Read only state.
     */
    render(state) {
        const { active, disabled, label } = state;

        super.render(state);

        this.node.classList.toggle("button--active", Boolean(active));

        if (disabled === true) {
            this.node.setAttribute("disabled", true);
        } else if (disabled === false) {
            this.node.removeAttribute("disabled");
        }

        if (label) {
            this.node.innerHTML = `${this.node.children[0]?.outerHTML} ${label}`;
        }
    }
}
