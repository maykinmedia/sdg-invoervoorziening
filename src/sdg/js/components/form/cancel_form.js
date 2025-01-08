import { FormComponent } from "./abstract/form_component";

/** @type {NodeListOf<HTMLAnchorElement>} */
const FORM_CANCEL_BUTTON = document.querySelectorAll("#cancel-button");

/**
 * Button allow the user to take over the reference text in all localized fields at the same time.
 */
class CancelFormButton extends FormComponent {
    constructor(node) {
        super(node);
        this.errorMessage =
            "Weet je zeker dat je wilt annuleren? Niet-opgeslagen wijzigingen gaan mogelijk verloren.";
    }

    bindEvents() {
        super.bindEvents();

        // Listen for form changes and add `data-changes` attribute.
        this.getForm().addEventListener(
            "input",
            this.addHasChangesAttribute.bind(this),
            { once: true }
        );
        this.getForm().addEventListener(
            "change",
            this.addHasChangesAttribute.bind(this),
            { once: true }
        );
    }

    /**
     * Add `data-changes='true'` to the form.
     */
    addHasChangesAttribute() {
        this.getForm().dataset.changes = true;
    }

    /**
     * Gets called when this.node gets clicked.
     * @param {MouseEvent} event
     */
    onClick(event) {
        // Show confirm alert when form has `data-changes='true'`
        if (this.getForm().dataset.changes === "true")
            if (!confirm(this.errorMessage)) {
                // When declined skip redirect and keep editing.
                return event.preventDefault();
            }
    }
}

// Start!
[...FORM_CANCEL_BUTTON].forEach((node) => new CancelFormButton(node));
