import applyMarkdownEditors from './markdown';
import showdown from 'showdown';

const converter = new showdown.Converter();
const forms = document.querySelectorAll(".form__has-reference");

const availableEditors = applyMarkdownEditors(".markdownx textarea");

class FormWithReference {
    constructor(node) {
        this.node = node;
        this.referenceForm = this.node.querySelector(".form__reference");
        this.formCells = this.node.querySelectorAll(".form__cell");

        [...this.formCells].forEach(cell => {
            const formInput = cell.querySelector(".form__input");

            const formReferenceBtn = cell.querySelector(".form__reference-btn");
            formReferenceBtn.addEventListener("click", (event) => {
                event.preventDefault();

                const referenceValue = this.referenceForm.content.getElementById(formInput.id).value;
                if (availableEditors.hasOwnProperty(formInput.id)) {
                    availableEditors[formInput.id].setData(referenceValue);
                } else {
                    formInput.value = referenceValue;
                }
            });

            const formDisplayBtn = cell.querySelector(".form__display-btn");
            formDisplayBtn.addEventListener("click", (event) => {
                event.preventDefault();
                const icon = formDisplayBtn.querySelector("svg");

                const existingDisplay = cell.querySelector(".reference__display");
                if (existingDisplay) {
                    icon.classList.add("fa-chevron-up");
                    existingDisplay.remove();
                } else {
                    icon.classList.add("fa-chevron-down");
                    const referenceField = this.referenceForm.content.getElementById(formInput.id);
                    const displayField = document.createElement("div");
                    displayField.classList.add("reference__display", "form__input", "form__input--disabled");
                    displayField.innerHTML = converter.makeHtml(referenceField.value);
                    cell.appendChild(displayField);
                }
            });

        });
    }
}

[...forms].forEach(form => new FormWithReference(form));
