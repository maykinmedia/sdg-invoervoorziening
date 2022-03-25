const form = document.querySelector(".form__general");

class GenericForm {

    setUpDynamicProductAanwezig() {
        const input = this.node.querySelector("[name=product_aanwezig]");
        const dependency = this.node.querySelector("[name=product_aanwezig_toelichting]");

        const displayFunc = (input, dependency) => {
            if (input.value === "false") {
                dependency.disabled = false;
                if (!dependency.value)
                    dependency.value = dependency.parentElement.dataset.defaultText;
            } else {
                dependency.disabled = true;
            }
        };

        displayFunc(input, dependency);
        input.addEventListener("change", (event) => {
            displayFunc(event.target, dependency);
        });
    }

    setUpDynamicProductValtOnder() {
        const select = document.querySelector("#id_product_valt_onder");
        const dependency = document.querySelector('[id$="product_valt_onder_toelichting"]').closest(".form__language-wrapper");

        const displayFunc = (select, dependency) => {
            if (select.selectedIndex > 0) {
                dependency.style.display = "block";
                const controls = dependency.querySelectorAll(".form__control");
                controls.forEach(element => {
                    const textarea = element.querySelector("textarea");
                    if (!textarea.value) {
                        const defaultExplanation = document.querySelector(`.form__reference-${element.lang}`).dataset.defaultToelichting;
                        const explanation = defaultExplanation.replace(/\[product\]/g, select.options[select.selectedIndex].text);
                        textarea.value = explanation;
                    }
                });
            } else {
                dependency.style.display = "none";
            }
            ;
        };

        displayFunc(select, dependency);
        select.addEventListener("change", (event) => {
            displayFunc(event.target, dependency);
        });
    }

    constructor(node) {
        this.node = node;
        this.setUpDynamicProductAanwezig();
        this.setUpDynamicProductValtOnder();
    }

}

if (form) {
    new GenericForm(form);
}
