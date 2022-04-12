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

    setUpDynamicProductAanwezig() {
        const input = this.node.querySelector("[name=product_aanwezig]");
        const dependency = this.getClarificationField().closest(".form__language-wrapper");

        const displayFunc = (displayDependency) => {
            if (input.selectedIndex === 2) {
                this.displayBlock(displayDependency)
                const controls = displayDependency.querySelectorAll(".form__control")
                controls.forEach(element => {
                    const textarea = element.querySelector("textarea");
                    if (!textarea.value) {
                        const defaultExplanation = document.querySelector(`.form__reference-${element.lang}`).dataset.productAanwezigToelichting;
                        textarea.value = defaultExplanation;
                    }
                });
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
                        return
                    }

                    this.displayBlock(dependency)
                })
            };
        };

        displayFunc(input, dependency);
        input.addEventListener("change", () => {
            displayFunc(dependency);
        });
    }

    setUpDynamicProductValtOnder() {
        const select = document.querySelector("#id_product_valt_onder");
        const dependency = document.querySelector('[id$="product_valt_onder_toelichting"]').closest(".form__language-wrapper");
        let previousSelectedProduct = select.options[select.selectedIndex].text;

        const displayFunc = (select, displayDependency) => {

            if (select.selectedIndex > 0) {
                this.displayBlock(displayDependency)
                const controls = displayDependency.querySelectorAll(".form__control");
                controls.forEach(element => {
                    const textarea = element.querySelector("textarea");
                    if (!textarea.value) {
                        const defaultExplanation = document.querySelector(`.form__reference-${element.lang}`).dataset.defaultToelichting;
                        const explanation = defaultExplanation.replace(/\[product\]/g, select.options[select.selectedIndex].text);
                        textarea.value = explanation;
                    }
                });
            } else {
                const controls = displayDependency.querySelectorAll(".form__control")
                let emptyOrDefault = 0
                controls.forEach((element, index, array) => {
                    const textarea = element.querySelector("textarea");
                    const defaultExplanation = document.querySelector(`.form__reference-${element.lang}`).dataset.defaultToelichting;
                    const explanation = defaultExplanation.replace(/\[product\]/g, previousSelectedProduct);

                    if (!textarea.value || textarea.value === explanation) {
                        emptyOrDefault += 1
                    }

                    if (emptyOrDefault == 2) {
                        this.displayHidden(dependency)
                        this.emptyFieldValues([array[index - 1], element])
                        return
                    }

                    this.displayBlock(dependency)
                })
            };

            if (select.options[select.selectedIndex].text !== previousSelectedProduct) {
                previousSelectedProduct = select.options[select.selectedIndex].text
            }
        };

        displayFunc(select, dependency);
        select.addEventListener("change", (event) => {
            displayFunc(event.target, dependency);
        });
    }
}

if (form) {
    new GenericForm(form);
}
