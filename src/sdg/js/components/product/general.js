const generalForms = document.querySelectorAll(".form__general");

class GeneralForm {

    setUpDynamicProductAanwezig() {
        const input = this.node.querySelector("[name=product_aanwezig]");
        const dependency = this.node.querySelector("[name=product_aanwezig_toelichting]")

        const displayFunc = (input, dependency) => {
            input.value === "false" ? dependency.disabled = false : dependency.disabled = true;
        };

        displayFunc(input, dependency);
        input.addEventListener("change", (event) => {
            displayFunc(event.target, dependency);
        });
    }

    setUpDynamicProductValtOnder() {
        const select = document.querySelector("#id_product_valt_onder");
        const dependencies = [...document.querySelectorAll('[id$="product_valt_onder_toelichting"]')]
            .map(e => e.parentElement.parentElement.parentElement);

        const displayFunc = (select, dependencies) => {
            select.selectedIndex > 0 ? dependencies.forEach(e => e.style.display = "table-row") : dependencies.forEach(e => e.style.display = "none");
        };

        displayFunc(select, dependencies);
        select.addEventListener("change", (event) => {
            displayFunc(event.target, dependencies);
        });
    }

    constructor(node) {
        this.node = node;
        this.setUpDynamicProductAanwezig();
        this.setUpDynamicProductValtOnder();
    }
}

[...generalForms].forEach(form => new GeneralForm(form));
