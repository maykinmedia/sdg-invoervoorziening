import * as diff from "../diff";

const {availableEditors} = require("../markdown");
import showdown from 'showdown';

const converter = new showdown.Converter();
const specificForms = document.querySelectorAll(".form__has-reference");

class FormWithReference {

    setValue(formInput, referenceValue) {
        if (availableEditors.hasOwnProperty(formInput.id)) {
            availableEditors[formInput.id].setData(referenceValue);
        } else {
            formInput.value = referenceValue;
        }
    }

    setupReferenceButton(cell) {
        // Setup a button that writes the reference to the cell input.

        const formReferenceBtn = cell.querySelector(".form__reference-btn");

        if (formReferenceBtn) {
            formReferenceBtn.addEventListener("click", (event) => {
                event.preventDefault();

                const formInput = cell.querySelector(".form__input");
                const referenceValue = this.referenceForm.content.getElementById(formInput.id).value;
                if (referenceValue) {
                    this.setValue(formInput, referenceValue);
                    // Trigger a change event on the field
                    const event = new Event('change');
                    formInput.dispatchEvent(event);
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
                    const previousReferenceField = this.previousReferenceForm.content.getElementById(formInput.id);

                    if (referenceField.value) {

                        const template = document.importNode(this.displayTemplate.content.children[0], true);
                        const templateDisplay = template.querySelector(".reference__display--content");
                        templateDisplay.innerHTML = converter.makeHtml(referenceField.value);
                        cell.appendChild(template);

                        // enable diff button
                        new diff.DiffButton(
                            template.querySelector(".diff"),
                            {
                                "cellValueElement": templateDisplay,
                                "previousVersionData": {
                                    "title": this.previousReferenceForm.dataset.title,
                                    "input": previousReferenceField,
                                },
                                "currentVersionData": {
                                    "title": this.referenceForm.dataset.title,
                                    "input": referenceField,
                                },
                                "versionsPanel": cell.parentElement.parentElement.querySelector(".reference__display--versions"),
                            }
                        );
                    }
                }

            });
        }
    }

    setupDiffButton(cell) {
        /*
        Setup a button that displays a diff between the current value and the reference text in the cell.
         */

        const formDiffBtn = cell.querySelector(".form__diff-btn");
        const formInput = cell.querySelector(".form__input");

        if (this.referenceForm && formDiffBtn && formInput) {
            const referenceInput = this.referenceForm.content.getElementById(formInput.id);
            const field = cell.querySelector(".tabs__table-cell--field");

            formInput.differ = new diff.DiffButton(
                formDiffBtn,
                {
                    "cellValueElement": field,
                    "previousVersionData": {
                        "title": this.referenceForm.dataset.title,
                        "input": referenceInput,
                    },
                    "currentVersionData": {
                        "title": "Huidige",
                        "input": formInput,
                    },
                    "versionsPanel": cell.querySelector(".tabs__table-cell--versions"),
                }
            );
            diff.addChangeListener(formInput);
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
            this.setupDiffButton(cell);
        });
    }
}

// TODO: find a better way to do this (e.g. listener after ckeditor is fully loaded)
setTimeout(() => {
    [...specificForms].forEach(form => new FormWithReference(form));
}, 2000);
