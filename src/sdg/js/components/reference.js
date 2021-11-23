const {availableEditors} = require("./markdown");
import showdown from 'showdown';

const converter = new showdown.Converter();
const specificForms = document.querySelectorAll(".form__has-reference");

class FormWithReference {
    setupReferenceButton(cell) {
        // Setup a button that writes the reference to the cell input.

        const formReferenceBtn = cell.querySelector(".form__reference-btn");
        const formInput = cell.querySelector(".form__input");

        if (formReferenceBtn) {
            formReferenceBtn.addEventListener("click", (event) => {
                event.preventDefault();

                const referenceValue = this.referenceForm.content.getElementById(formInput.id).value;
                if (referenceValue) {
                    if (availableEditors.hasOwnProperty(formInput.id)) {
                        availableEditors[formInput.id].setData(referenceValue);
                    } else {
                        formInput.value = referenceValue;
                    }
                }
            });
        }
    }

    setupDisplayButton(cell) {
        // Setup a button that displays a read-only reference text in the cell.

        const formDisplayBtn = cell.querySelector(".form__display-btn");
        const formInput = cell.querySelector(".form__input");

        if (formDisplayBtn) {
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
                    if (referenceField.value) {
                        const displayField = document.createElement("div");
                        displayField.classList.add("reference__display", "form__input", "form__input--disabled");
                        displayField.innerHTML = converter.makeHtml(referenceField.value);
                        cell.appendChild(displayField);
                    }
                }
            });
        }
    }

    constructor(node) {
        this.node = node;
        this.referenceForm = document.querySelector(this.node.dataset.reference);
        this.formCells = this.node.querySelectorAll(".tabs__table-cell");

        [...this.formCells].forEach(cell => {
            this.setupReferenceButton(cell);
            this.setupDisplayButton(cell);
        });
    }
}

[...specificForms].forEach(form => new FormWithReference(form));
