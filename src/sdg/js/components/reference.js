const forms = document.querySelectorAll(".form__has-reference");

class FormWithReference {
    constructor(node) {
        this.node = node;
        this.referenceForm = this.node.querySelector(".form__reference");
        this.formCell = this.node.querySelectorAll(".form__cell");

        [...this.formCell].forEach(cell => {
            const formInput = cell.querySelector(".form__input");
            const formReferenceBtn = cell.querySelector(".form__reference-btn");
            formReferenceBtn.addEventListener("click", (event) => {
                event.preventDefault();
                const referenceValue = this.referenceForm.content.getElementById(formInput.id).value
                if (mdeObject.hasOwnProperty(formInput.id)) {
                    mdeObject[formInput.id].value(referenceValue);
                } else {
                    formInput.value = referenceValue;
                }
            })
        });
    }
}

[...forms].forEach(form => new FormWithReference(form));
