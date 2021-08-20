const selectionTabs = document.querySelectorAll(".selection__tab");
const selectionContents = document.querySelectorAll(".selection__tab-content");

class SelectionToggle {
    constructor(node) {
        this.node = node;

        this.node.addEventListener("click", (event) => {
            event.preventDefault();
            [...selectionContents].forEach(selectionContent => selectionContent.classList.remove("selection__tab-content--active"));
            [...selectionTabs].forEach(selectionTab => selectionTab.classList.remove("selection__tab--selected"));
            event.currentTarget.classList.add("selection__tab--selected");
            const selectedContent = document.getElementById(event.currentTarget.dataset.id);
            selectedContent.classList.add("selection__tab-content--active");
        });
    }
}

[...selectionTabs].forEach(selectionTab => new SelectionToggle(selectionTab));
