const {availableEditors} = require("./markdown");

const disabledCellClass = "form__cell--disabled";

const disabledCells = document.querySelectorAll(`.${disabledCellClass}`);

const forms = document.querySelectorAll(".form");

function changeReadOnly(cell, readOnly) {
    // Modify the readonly status of the cell inputs.

    readOnly ? cell.classList.add(disabledCellClass) : cell.classList.remove(disabledCellClass);

    cell.querySelectorAll('input, textarea').forEach(element => {
        element.readOnly = readOnly;
        element.disabled = readOnly;
    });

    const formInput = cell.querySelector(".form__input");
    if (availableEditors.hasOwnProperty(formInput.id)) {
        availableEditors[formInput.id].isReadOnly = readOnly;
    }

}

class FormWithEditToggle {
    setupEditButton(cell) {
        // Setup an edit button that enables the cell input.

        const editButton = cell.querySelector(".form__edit-btn");
        if (editButton) {
            editButton.addEventListener("click", (event) => {
                event.preventDefault();
                if (cell.classList.contains(disabledCellClass)) {
                    changeReadOnly(cell, false);
                } else {
                    changeReadOnly(cell, true);
                }
            });
        }
    }

    constructor(node) {
        this.node = node;
        this.formCells = this.node.querySelectorAll(".tabs__table-cell");

        [...this.formCells].forEach(cell => {
            this.setupEditButton(cell);
        });
    }
}

[...forms].forEach(form => new FormWithEditToggle(form));
[...disabledCells].forEach(cell => changeReadOnly(cell, true));
