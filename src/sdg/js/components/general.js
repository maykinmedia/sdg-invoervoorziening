const generalForms = document.querySelectorAll(".form__general");

class GeneralForm {

    setUpDynamicTextarea() {
        const input = this.node.querySelector("[name=product_aanwezig]");
        const textarea = this.node.querySelector("[name=product_aanwezig_toelichting]")

        input.addEventListener("change", (event) => {
            event.target.value === "false" ? textarea.disabled = false : textarea.disabled = true;
        });
    }

    constructor(node) {
        this.node = node;
        this.setUpDynamicTextarea();
    }
}

[...generalForms].forEach(form => new GeneralForm(form));
