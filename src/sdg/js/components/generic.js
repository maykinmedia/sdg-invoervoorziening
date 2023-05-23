const form = document.querySelector('.form');

class GenericForm {
    /**
     * Constructor method.
     * @param {HTMLFormElement} node
     */
    constructor(node) {
        /** @type {HTMLFormElement} */
        this.node = node;
        this.display = {
            "valtOnder": false,
            "aanwezig": false
        }

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

    collapseExpand() {
        const formSpecific = document.querySelector(".form__specific");
        const formSpecificClassList = formSpecific.classList

        if (!this.display.valtOnder || !this.display.aanwezig) {
            formSpecific.style.pointerEvents = "none";
            formSpecificClassList.add("tabs__table--hidden")
            formSpecificClassList.add("form__specific--hidden")
        }

        if (this.display.valtOnder  && this.display.aanwezig) {
            formSpecific.style.pointerEvents = "all";
            formSpecificClassList.remove("tabs__table--hidden")
            formSpecificClassList.remove("form__specific--hidden")
        }
    }

    displayHidden(dependency, field) {
        dependency.style.display = "none";
        this.display[field] = true
        this.collapseExpand()
    }

    displayBlock(dependency, field) {
        dependency.style.display = "block";
        this.display[field] = false
        this.collapseExpand()
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

    setUpDynamicProductAanwezig() {
        const input = this.node.querySelector("[name=product_aanwezig]");
        const dependency = this.getClarificationField().closest(".form__language-wrapper");

        if (input) {

            const displayFunc = (displayDependency) => {
                if (input.selectedIndex === 2) {
                    this.displayBlock(displayDependency, "aanwezig")
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
                            this.displayHidden(dependency, "aanwezig")
                            this.emptyFieldValues([array[index - 1], element])
                            return
                        }

                        this.displayBlock(dependency, "aanwezig")
                    })
                };
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
                    this.displayBlock(displayDependency, "valtOnder")
                    const controls = displayDependency.querySelectorAll(".form__control");
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
                                this.displayHidden(dependency, "valtOnder")
                                this.emptyFieldValues([controls[index - 1], element])
                                previousSelectedProduct = null
                                return
                            }

                            this.displayBlock(dependency, "valtOnder")
                        } else if (previousSelectedProduct == null && textarea.value == "") {
                            this.displayHidden(dependency, "valtOnder")
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
