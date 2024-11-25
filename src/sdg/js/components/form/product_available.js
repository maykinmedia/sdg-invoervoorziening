import { ClarificationFieldComponent } from "./abstract/clarification_field_component";

/** @type {NodeListOf<HTMLSelectElement>} */
const PRODUCT_AANWEZIG_SELECTS = document.querySelectorAll(
    "#id_product_aanwezig"
);

const PRODUCT_AANWEZIG_QUESTION =
    "Weet u zeker dat u dit product niet aanbiedt?\nAls u 'OK' antwoordt worden alle teksten leeggemaakt.";

/**
 * Button allow the user to take over the reference text in all localized fields at the same time.
 */
class ProductAvailable extends ClarificationFieldComponent {
    /**
     * Constructor method.
     * @param {HTMLSelectElement} node
     */
    constructor(node) {
        super(node);
        this.dependency = this.getAvailabilityClarificationFormField();
        this.previousSelectedIndex = this.node.selectedIndex;
    }

    /**
     * Gets called after the first render cycle.
     */
    onMount() {
        super.onMount();
        this.handle();
    }

    /**
     * Binds events to callbacks.
     */
    bindEvents() {
        this.node.addEventListener("change", this.handle.bind(this));
    }

    /**
     * Update the values of the text areas.
     */
    updateValues() {
        Object.entries(this.getAvailabilityClarificationFields()).forEach(
            ([language, node]) => {
                if (node.value) return;
                const defaultExplanation =
                    this.getCurrentReferenceForm(language).dataset
                        .productAanwezigToelichting;
                node.value = defaultExplanation;
            }
        );
    }

    /**
     * Gets called on change and on mount.
     */
    handle() {
        if (this.node.selectedIndex === 2) {
            this.availability = true;
            if (this.node.selectedIndex != this.previousSelectedIndex) {
                if (confirm(PRODUCT_AANWEZIG_QUESTION)) {
                    this.resetSpecifiekeGegevens();
                } else {
                    this.node.selectedIndex = this.previousSelectedIndex;
                    return;
                }
            }

            this.showClarificationField();
            this.updateValues();
        } else {
            this.availability = false;
            this.hideClarificationField();
        }

        this.previousSelectedIndex = this.node.selectedIndex;
    }
}

// Start!
[...PRODUCT_AANWEZIG_SELECTS].forEach((node) => new ProductAvailable(node));
