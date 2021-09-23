const referenceButtons = document.querySelectorAll(".tabs__table");

class ReferenceButton {
    constructor(node) {
        this.node = node;
        this.items = node.querySelectorAll(".tabs__table-help");

        [...this.items].forEach(item => {
            item.addEventListener("click", (event) => {
                // ...
            });
        });
    }
}

[...referenceButtons].forEach(referenceButton => new ReferenceButton(referenceButton));
