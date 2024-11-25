import { ClarificationFieldComponent } from "./abstract/clarification_field_component";
import { fetchCmsApiProductTranslationName } from "./utils";

/** @type {NodeListOf<HTMLSelectElement>} */
const PRODUCT_VALT_ONDER_SELECT = document.querySelectorAll(
    "#id_product_valt_onder"
);

const PRODUCT_VALT_ONDER_QUESTION =
    "Weet u zeker dat dit product onder een ander product valt?\nAls u 'OK' antwoordt worden alle teksten leeggemaakt.";

/**
 * Button allow the user to take over the reference text in all localized fields at the same time.
 */
class ProductValtOnder extends ClarificationFieldComponent {
    /**
     * Constructor method.
     * @param {HTMLSelectElement} node
     */
    constructor(node) {
        super(node);
        this.dependency = this.getFallsUnderClarificationFormField();
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
     * By updating the value an API request is made to the CMS API, to get the product translation name.
     */
    updateValues() {
        const productTranslations = fetchCmsApiProductTranslationName(
            this.node.value
        );

        Object.entries(this.getFallsUnderClarificationFields()).forEach(
            async ([language, node]) => {
                const defaultExplanation =
                    this.getCurrentReferenceForm(language).dataset
                        .defaultToelichting;

                try {
                    const translations = await productTranslations;
                    node.value = defaultExplanation.replace(
                        /\[product\]/g,
                        translations[language]
                    );
                } catch (error) {
                    node.value = defaultExplanation;
                }
            }
        );
    }

    /**
     * Gets called on change and on mount.
     */
    handle() {
        if (this.node.selectedIndex > 0) {
            this.fallsUnder = true;

            if (this.previousSelectedIndex == 0) {
                if (confirm(PRODUCT_VALT_ONDER_QUESTION)) {
                    this.resetSpecifiekeGegevens();
                    this.showClarificationField(this.dependency);
                } else {
                    this.node.selectedIndex = 0;
                    return;
                }
            }
            this.updateValues();
        } else {
            this.fallsUnder = false;
            this.hideClarificationField();
        }

        this.previousSelectedIndex = this.node.selectedIndex;
    }
}

// Start!
[...PRODUCT_VALT_ONDER_SELECT].forEach((node) => new ProductValtOnder(node));
