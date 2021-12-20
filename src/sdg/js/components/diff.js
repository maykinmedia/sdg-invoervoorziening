import {availableEditors} from "./markdown";
import ClassicEditor from "./ckeditor";

const Diff = require("text-diff");

export function getValue(input) {
    if (availableEditors.hasOwnProperty(input.id)) {
        return availableEditors[input.id].getData();
    }
    return input.value;
}

export function addChangeListener(input) {
    input.addEventListener("change", (event) => {
        event.target.differ.refresh();
    });
}


class DiffButton {

    refresh() {
        // Refresh the current value of the diff button
        this.default = this.cellValueElement.cloneNode(true);
        this.currentVersionData.input = this.cellValueElement.querySelector(".form__input");
    }

    displayDiff() {
        // Return the diff between the two versions.
        this.button.classList.add("form__diff-btn--enabled");
        const previousValue = this.previousVersionData.input.value;
        const currentValue = getValue(this.currentVersionData.input);
        const textDiff = this.diff.main(previousValue, currentValue);
        this.cellValueElement.innerHTML = this.diff.prettyHtml(textDiff).replace(/\\/g, "");
        this.versionsPanel.append(this.previousVersionTopElement);
        this.versionsPanel.append(this.currentVersionTopElement);
    }


    hideDiff() {
        this.button.classList.remove("form__diff-btn--enabled");

        const newElement = this.default.cloneNode(true);
        this.cellValueElement.replaceWith(newElement);
        this.cellValueElement = newElement;
        const input = this.cellValueElement.querySelector(".form__input");

        // Check if available editors includes element id
        if (availableEditors.hasOwnProperty(input.id)) {
            const initial = availableEditors[input.id].getData();
            // Replace available editor element with new element
            this.cellValueElement.querySelector(".ck-editor").remove();
            ClassicEditor.create(input).then(editor => {
                availableEditors[input.id].destroy();
                availableEditors[input.id] = editor;
                editor.setData(initial);
                editor.isReadOnly = true;
                // Trigger a change event on the field
                const event = new Event('change');
                input.dispatchEvent(event);
            });
        }

        if (input) {
            input.differ = this;
            addChangeListener(input);
        }

        while (this.versionsPanel.firstChild)
            this.versionsPanel.removeChild(this.versionsPanel.firstChild);
    }


    setUpDiffButton(node) {
        node.addEventListener("click", event => {
            event.preventDefault();
            debugger;
            // Check if the diff is already displayed.
            if (this.cellValueElement.isEqualNode(this.default)) {
                this.displayDiff();
            } else {
                this.hideDiff();
            }
        })
    }

    constructor(button, config = {
        "cellValueElement": null,
        "previousVersionData": {},
        "currentVersionData": {},
        "versionsPanel": null,
    }) {
        this.button = button;

        this.cellValueElement = config.cellValueElement;
        this.previousVersionData = config.previousVersionData;
        this.currentVersionData = config.currentVersionData;
        this.versionsPanel = config.versionsPanel;

        this.default = this.cellValueElement.cloneNode(true);

        this.currentVersionTopElement = document.createElement("ins");
        this.currentVersionTopElement.innerText = this.currentVersionData.title;

        this.previousVersionTopElement = document.createElement("del");
        this.previousVersionTopElement.innerText = this.previousVersionData.title;

        this.diff = new Diff();
        this.setUpDiffButton(this.button);
    }
}

export {DiffButton}
