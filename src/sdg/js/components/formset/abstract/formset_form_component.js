import { FormComponent } from "./form_component";

/**
 * Base class for implementing components within a formset update form.
 * @abstract
 */
export class FormsetFormComponent extends FormComponent {
    /**
     * Options object.
     * Use this to specify the options of the component.
     * @type {Object}
     */
    static options = {
        observe: true,
    };

    /**
     * Gets called after the first render cycle.
     * Use this to sync state with DOM on initial mount.
     */
    onMount() {
        super.onMount();
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
    }
}
