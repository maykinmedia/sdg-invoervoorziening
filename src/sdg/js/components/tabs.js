const tabsTabs = document.querySelectorAll(".tabs__tab");
const tabsContents = document.querySelectorAll(".tabs__tab-content");

class TabsToggle {
    constructor(node) {
        this.node = node;

        this.node.addEventListener("click", (event) => {
            if (event.target.dataset.id) {
                event.preventDefault();
                [...tabsContents].forEach(tabsContent => tabsContent.classList.remove("tabs__tab-content--active"));
                [...tabsTabs].forEach(tabsTab => tabsTab.classList.remove("tabs__tab--selected"));
                event.currentTarget.classList.add("tabs__tab--selected");
                const selectedContent = document.getElementById(event.currentTarget.dataset.id);
                selectedContent.classList.add("tabs__tab-content--active");
            }
        });
    }
}

[...tabsTabs].forEach(tabsTab => new TabsToggle(tabsTab));
