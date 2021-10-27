import Cookies from 'js-cookie';

const tabsTabs = document.querySelectorAll(".tabs__tab");
const tabsContents = document.querySelectorAll(".tabs__tab-content");

function toggleTab(target) {
    [...tabsContents].forEach(tabsContent => tabsContent.classList.remove("tabs__tab-content--active"));
    [...tabsTabs].forEach(tabsTab => tabsTab.classList.remove("tabs__tab--selected"));
    target.classList.add("tabs__tab--selected");
    const tabId = target.dataset.id;
    const selectedContent = document.getElementById(tabId);
    selectedContent.classList.add("tabs__tab-content--active");
    Cookies.set("tab_lang", tabId)
}

class TabsToggle {
    constructor(node) {
        this.node = node;

        this.node.addEventListener("click", (event) => {
            event.preventDefault();
            toggleTab(event.currentTarget);
        });
    }
}

[...tabsTabs].forEach(tabsTab => new TabsToggle(tabsTab));

