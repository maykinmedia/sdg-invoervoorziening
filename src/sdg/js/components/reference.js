import {DiffButton} from "./diff";

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
        /*
        Setup a button that displays a read-only reference text in the cell. With diff functionality.
         */

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
                    const currentVersionData = {
                        "title": this.referenceForm.dataset.title,
                        "text": referenceField.value
                    };

                    const previousReferenceField = this.previousReferenceForm.content.getElementById(formInput.id);
                    const previousVersionData = {
                        "title": this.previousReferenceForm.dataset.title,
                        "text": previousReferenceField.value
                    };

                    if (referenceField.value) {

                        const template = document.importNode(this.displayTemplate.content.children[0], true);
                        const templateDisplay = template.querySelector(".reference__display--content");
                        templateDisplay.innerHTML = converter.makeHtml(referenceField.value);
                        cell.appendChild(template);

                        // enable diff button
                        new DiffButton(
                            template.querySelector(".diff"),
                            templateDisplay.innerHTML,
                            previousVersionData,
                            currentVersionData,
                        );

                    }
                }

            });
        }
    }

    constructor(node) {
        this.node = node;

        this.referenceForm = document.querySelector(this.node.dataset.reference);
        this.previousReferenceForm = document.querySelector(this.node.dataset.previousreference);

        this.formCells = this.node.querySelectorAll(".tabs__table-cell");
        this.displayTemplate = document.querySelector(".form__reference--display-template");

        [...this.formCells].forEach(cell => {
            this.setupReferenceButton(cell);
            this.setupDisplayButton(cell);
        });
    }
}

[...specificForms].forEach(form => new FormWithReference(form));
