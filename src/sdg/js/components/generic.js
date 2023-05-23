import {availableEditors} from './markdown'
const form = document.querySelector('.form');

class GenericForm {
    /**
     * Constructor method.
     * @param {HTMLFormElement} node
     */
    constructor(node) {
        /** @type {HTMLFormElement} */
        this.node = node;

        if(!this.isGenericForm()) {
            return;  // Not a generic form.
        }

        if (this.node) {
            this.setUpDynamicProductAanwezig();
            this.setUpDynamicProductValtOnder();
        }
    }

    /**
     * Returns whether `this.node` represents a generic form based on node tree.
     * @return {boolean}
     */
    isGenericForm() {
        return Boolean(this.getClarificationField());
    }

    /**
     * Returns clarification field (if found).
     * @return {(Element|null)}
     */
    getClarificationField() {
        return this.node.querySelector('[id$="product_aanwezig_toelichting"]');
    }

    displayHidden(dependency) {
        dependency.style.display = "none";
    }

    displayBlock(dependency) {
        dependency.style.display = "block";
    }

    emptyFieldValues(fields) {
        fields.forEach((item) => {
            const textarea = item.querySelector("textarea");
            textarea.value = ""
        })
    }

    async getProductTranslationName(productId, language) {
        // SubPath is a globally defined constant.
        const url = `${window.location.origin}${SubPath}/cmsapi/translation/?product_id=${productId}&taal=${language}`
        const translationJsonResults = await fetch(url)
            .then(response => response.json())
            .then(data => data.results[0])

        if (translationJsonResults) {

            if (translationJsonResults.productTitel) {
                return translationJsonResults.productTitel
            }
            return translationJsonResults.generiekProduct
        }
        return ""
    }

    resetSpecefiekeGegevens() {
        const none_markdown_editor_fields = [
            "[name=vertalingen-0-product_titel_decentraal]",
            "[name=vertalingen-1-product_titel_decentraal]",
            "[name=vertalingen-0-decentrale_procedure_link]",
            "[name=vertalingen-1-decentrale_procedure_link]",
            "[name=vertalingen-0-decentrale_procedure_label]",
            "[name=vertalingen-1-decentrale_procedure_label]"
        ]
        const array_fields = [
            "[name=vertalingen-0-verwijzing_links]",
            "[name=vertalingen-1-verwijzing_links]",
        ]
        const markdown_editor_fields = document.querySelectorAll('.markdownx textarea');

        none_markdown_editor_fields.forEach((field) => {
            let input_field = this.node.querySelector(field);
            if (input_field) {
                input_field.value = ''
            }
        })

        array_fields.forEach((field) => {
            let input_fields = this.node.querySelectorAll(field);
            input_fields.forEach((input_field) => {
                if (input_field) {
                    input_field.value = ''
                }
            })
        })

        markdown_editor_fields.forEach((field) => {
            field.value = ''
        })

        Object.values(availableEditors).forEach((instance) => {
            instance.editor.setData("")
        })
    }

    setUpDynamicProductAanwezig() {
        const input = this.node.querySelector("[name=product_aanwezig]");
        const dependency = this.getClarificationField().closest(".form__language-wrapper");

        if (input) {
            let previousIndex = input.selectedIndex;

            const displayFunc = async (displayDependency) => {
                if (input.selectedIndex === 2) {
                    if (confirm("Weet u zeker dat u dit product niet aanbiedt?\nAls u 'OK' antwoordt worden alle teksten leeggemaakt.")) {
                        const controls = displayDependency.querySelectorAll(".form__control")
                        this.resetSpecefiekeGegevens();
                        this.displayBlock(displayDependency)
                        controls.forEach(element => {
                            const textarea = element.querySelector("textarea");
                            if (!textarea.value) {
                                const defaultExplanation = document.querySelector(`.form__reference-${element.lang}`).dataset.productAanwezigToelichting;
                                textarea.value = defaultExplanation;
                            }
                        });
                    } else {
                        input.selectedIndex = previousIndex;
                    }
                } else {
                    const controls = displayDependency.querySelectorAll(".form__control")
                    let emptyOrDefault = 0
                    controls.forEach((element, index, array) => {
                        const textarea = element.querySelector("textarea");
                        const defaultExplanation = document.querySelector(`.form__reference-${element.lang}`).dataset.productAanwezigToelichting;

                        if (!textarea.value || textarea.value === defaultExplanation) {
                            emptyOrDefault += 1
                        }

                        if (emptyOrDefault == 2) {
                            this.displayHidden(dependency)
                            this.emptyFieldValues([array[index - 1], element])
                            previousIndex = 0;
                            return
                        }

                        this.displayBlock(dependency)
                    })
                };

                previousIndex = input.selectedIndex;
            };

            displayFunc(dependency);
            input.addEventListener("change", () => {
                displayFunc(dependency);
            });
        };
    }

    setUpDynamicProductValtOnder() {
        const select = document.querySelector("#id_product_valt_onder");
        const dependency = document.querySelector('[id$="product_valt_onder_toelichting"]').closest(".form__language-wrapper");

        if (select) {
            let previousSelectedProduct = null;
            const displayFunc = async (select, displayDependency) => {
                if (select.selectedIndex > 0) {
                    const controls = displayDependency.querySelectorAll(".form__control");

                    if (previousSelectedProduct == null) {
                        if (confirm("Weet u zeker dat dit product onder een ander product valt?\nAls u 'OK' antwoordt worden alle teksten leeggemaakt.")) {
                            this.resetSpecefiekeGegevens();
                            this.displayBlock(displayDependency)
                        } else {
                            previousSelectedProduct = null;
                            select.selectedIndex = 0;
                            return
                        }
                    }

                    for (const element of controls) {
                        previousSelectedProduct = select.value;
                        const textarea = element.querySelector("textarea");
                        const defaultExplanation = document.querySelector(`.form__reference-${element.lang}`).dataset.defaultToelichting;
                        const explanation = defaultExplanation.replace(/\[product\]/g, await this.getProductTranslationName(select.value, element.lang));
                        textarea.value = explanation;
                    };
                } else {
                    const controls = displayDependency.querySelectorAll(".form__control")
                    let emptyOrDefault = 0
                    let index = 0
                    for (const element of controls) {
                        const textarea = element.querySelector("textarea");
                        const defaultExplanation = document.querySelector(`.form__reference-${element.lang}`).dataset.defaultToelichting;
                        if (previousSelectedProduct != null) {
                            const explanation = defaultExplanation.replace(/\[product\]/g, await this.getProductTranslationName(previousSelectedProduct, element.lang));

                            if (!textarea.value || textarea.value === explanation) {
                                emptyOrDefault += 1
                            }

                            if (emptyOrDefault == 2) {
                                this.displayHidden(dependency)
                                this.emptyFieldValues([controls[index - 1], element])
                                previousSelectedProduct = null
                                return
                            }

                            this.displayBlock(dependency)
                        } else if (previousSelectedProduct == null && textarea.value == "") {
                            this.displayHidden(dependency)
                        }
                        index++
                    }
                };
            };

            displayFunc(select, dependency);
            select.addEventListener("change", (event) => {
                displayFunc(event.target, dependency);
            });
        };
    }
}

if (form) {
    new GenericForm(form);
}
