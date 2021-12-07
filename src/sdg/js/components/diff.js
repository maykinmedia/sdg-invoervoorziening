const Diff = require("text-diff");

class DiffButton {

    displayDiff() {
        // Return the diff between the two versions.
        const textDiff = this.diff.main(this.previousVersionData.text, this.currentVersionData.text);
        this.cellValueElement.innerHTML = this.diff.prettyHtml(textDiff).replace(/\\/g, "");
        this.versionsPanel.append(this.previousVersionTopElement);
        this.versionsPanel.append(this.currentVersionTopElement);
    }


    hideDiff() {
        this.cellValueElement.innerHTML = this.defaultHtml;
        while (this.versionsPanel.firstChild)
            this.versionsPanel.removeChild(this.versionsPanel.firstChild);
    }


    setUpDiffButton(node) {
        node.addEventListener("click", event => {
            event.preventDefault();
            // Check if the diff is already displayed.
            if (this.cellValueElement.innerHTML === this.defaultHtml) {
                this.displayDiff();
            } else {
                this.hideDiff();
            }
        })
    }

    constructor(node, defaultHtml, previousVersionData, currentVersionData) {
        this.node = node;
        this.cell = node.parentElement.parentElement;
        this.versionsPanel = this.cell.querySelector(".reference__display--versions");
        this.cellValueElement = this.cell.querySelector(".reference__display--content");

        this.defaultHtml = defaultHtml;
        this.previousVersionData = previousVersionData;
        this.currentVersionData = currentVersionData;

        this.currentVersionTopElement = document.createElement("ins");
        this.currentVersionTopElement.innerText = this.currentVersionData.title;

        this.previousVersionTopElement = document.createElement("del");
        this.previousVersionTopElement.innerText = this.previousVersionData.title;

        this.diff = new Diff();
        this.setUpDiffButton(node);
    }
}

export {DiffButton}
