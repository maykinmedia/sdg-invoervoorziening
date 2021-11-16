import applyMarkdownEditors from './markdown';
import showdown from 'showdown';

const converter = new showdown.Converter();
const forms = document.querySelectorAll(".form__has-reference");

const availableEditors = applyMarkdownEditors(".markdownx textarea");

const disabledCellClass = "form__cell--disabled";
const disabledCells = document.querySelectorAll(`.${disabledCellClass}`);

function disableCellInputs(cell) {
    // Disable all inputs in the cell

    cell.querySelectorAll('input, textarea').forEach(element => {
        element.readOnly = true;
        element.disabled = true;
    });

    const formInput = cell.querySelector(".form__input");
    if (availableEditors.hasOwnProperty(formInput.id)) {
        availableEditors[formInput.id].isReadOnly = true;
    }
}

function enableCellInputs(cell) {
    // Enable all inputs in the cell

    cell.querySelectorAll('input, textarea').forEach(element => {
        element.readOnly = false;
        element.disabled = false;
    });

    const formInput = cell.querySelector(".form__input");
    if (availableEditors.hasOwnProperty(formInput.id)) {
        availableEditors[formInput.id].isReadOnly = false;
    }
}

class FormWithReference {
    setupReferenceButton(cell) {
        // Setup a button that writes the reference to the cell input.

        const formReferenceBtn = cell.querySelector(".form__reference-btn");
        const formInput = cell.querySelector(".form__input");

        formReferenceBtn.addEventListener("click", (event) => {
            event.preventDefault();

            const referenceValue = this.referenceForm.content.getElementById(formInput.id).value;
            if (availableEditors.hasOwnProperty(formInput.id)) {
                availableEditors[formInput.id].setData(referenceValue);
            } else {
                formInput.value = referenceValue;
            }
        });
    }

    setupDisplayButton(cell) {
        // Setup a button that displays a read-only reference text in the cell.

        const formDisplayBtn = cell.querySelector(".form__display-btn");
        const formInput = cell.querySelector(".form__input");

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

    setupEditButton(cell) {
        // Setup an edit button that enables the cell input.

        const editButton = cell.querySelector(".form__edit-btn");

        editButton.addEventListener("click", (event) => {
            event.preventDefault();
            if (cell.classList.contains(disabledCellClass)) {
                cell.classList.remove(disabledCellClass);
                enableCellInputs(cell);
            } else {
                cell.classList.add(disabledCellClass);
                disableCellInputs(cell);
            }
        });
    }


    constructor(node) {
        this.node = node;
        this.referenceForm = document.querySelector(this.node.dataset.reference);
        this.formCells = this.node.querySelectorAll(".form__cell");

        [...this.formCells].forEach(cell => {
            this.setupReferenceButton(cell);
            this.setupDisplayButton(cell);
            this.setupEditButton(cell);
        });
    }
}

[...forms].forEach(form => new FormWithReference(form));
[...disabledCells].forEach(cell => disableCellInputs(cell));
