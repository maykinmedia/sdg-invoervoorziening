import { availableEditors } from "../../markdown";
import { FormComponent } from "./form_component";

/**
 * Base class for implementing components within the update form.
 * @abstract
 */
export class ClarificationFieldComponent extends FormComponent {
    /**
     * Constructor method.
     * @param {HTMLSelectElement} node
     */
    constructor(node) {
        super(node);
        this.node = node; // Same as in super(node), but this will overwrite the type HTMLElement with HTMLSelectElement.
        this.isReferenceForm = this.getForm().dataset.reference === "true";
    }

    /**
     * Shows the clarification field `this.dependency` and collapse specific form
     */
    showClarificationField() {
        this.dependency.style.display = "grid";
        this.collapseOrExpandSpecificForm(true);
    }

    /**
     * Hides the clarification field `this.dependency` and expands specific form
     */
    hideClarificationField() {
        this.dependency.style.display = "none";
        this.collapseOrExpandSpecificForm(false);
    }

    /**
     * Reset all the text areas, markdown fields and array fields inside the specific form.
     * Use fieldGroups to specify the fields to reset.
     */
    resetSpecifiekeGegevens() {
        const RESET_VALUE = "";

        const resetConfiguration = {
            noneMarkdown: {
                fields: [
                    "[name=vertalingen-0-product_titel_decentraal]",
                    "[name=vertalingen-1-product_titel_decentraal]",
                    "[name=vertalingen-0-decentrale_procedure_link]",
                    "[name=vertalingen-1-decentrale_procedure_link]",
                    "[name=vertalingen-0-decentrale_procedure_label]",
                    "[name=vertalingen-1-decentrale_procedure_label]",
                ],
                selectAll: false,
            },
            arrayFields: {
                fields: [
                    "[name=vertalingen-0-verwijzing_links]",
                    "[name=vertalingen-1-verwijzing_links]",
                ],
                selectAll: true,
            },
            markdown: {
                fields: [".markdownx textarea"],
                selectAll: true,
            },
        };

        Object.values(resetConfiguration).forEach((group) => {
            group.fields.forEach((field_class) => {
                if (group.selectAll) {
                    document.querySelectorAll(field_class).forEach((field) => {
                        field.value = RESET_VALUE;
                    });
                } else {
                    document.querySelector(field_class).value = RESET_VALUE;
                }
            });
        });

        Object.values(availableEditors).forEach((instance) => {
            instance.editor.setData(RESET_VALUE);
        });
    }

    /**
     * Collapse and remove pointer events or expand and add pointer events the specific form.
     * @param {boolean} collapse
     */
    collapseOrExpandSpecificForm(collapse) {
        const formSpecific = document.querySelector(".form__specific");
        const formSpecificClassList = formSpecific.classList;
        formSpecific.style.pointerEvents = collapse ? "none" : "all";
        formSpecificClassList.toggle("tabs__table--hidden", collapse);
        formSpecificClassList.toggle("form__specific--hidden", collapse);
    }

    /**
     * Returns an object containing all product_aanwezig_toelichting fields as value with the key as the language.
     * @returns { HTMLElement }
     */
    getAvailabilityClarificationFormField(child = undefined) {
        const availabilityClarificationField = this.getForm(
            child
        ).querySelector('[id$="product_aanwezig_toelichting"]');
        return this.getFormField(availabilityClarificationField);
    }

    /**
     * Returns an object containing all product_aanwezig_toelichting fields as value with the key as the language.
     * @returns { HTMLElement }
     */
    getFallsUnderClarificationFormField(child = undefined) {
        const fallsUnderClarificationField = this.getForm(child).querySelector(
            '[id$="product_valt_onder_toelichting"]'
        );
        return this.getFormField(fallsUnderClarificationField);
    }

    /**
     * Returns an object containing all product_aanwezig_toelichting fields as value with the key as the language.
     * @returns {{ [language: string]: HTMLElement} }
     */
    getAvailabilityClarificationFields(child = undefined) {
        const nodes = this.getForm(child).querySelectorAll(
            '[id$="product_aanwezig_toelichting"]'
        );
        return this._localizedGetter(nodes);
    }

    /**
     * Returns an object containing all product_valt_onder_toelichting fields as value with the key as the language.
     * @returns {{ [language: string]: HTMLElement} }
     */
    getFallsUnderClarificationFields(child = undefined) {
        const nodes = this.getForm(child).querySelectorAll(
            '[id$="product_valt_onder_toelichting"]'
        );
        return this._localizedGetter(nodes);
    }
}
