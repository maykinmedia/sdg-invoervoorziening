const filterContainers = document.querySelectorAll(".filter");

class Filter {
    showAllProducts() {
        this.accordeon.querySelectorAll(".products__item").forEach(element => {
            element.classList.remove("hidden");
        });
    }

    clearTextFilter() {
        // Clear text filter
        this.node.querySelector(".filter__input").value = "";
    }

    clearAllFilterButtons() {
        // Clear all filter buttons
        const filterButtons = this.node.querySelectorAll(".filter__button");
        filterButtons.forEach(item => {
            item.classList.add("filter__button--off");
        });
    }

    clearAllFilterGroups() {
        // Clear all filter buttons
        const filterCheckboxes = this.node.querySelectorAll(".filter__group--checkbox");
        filterCheckboxes.forEach(item => {
            item.checked = false;
        });
    }

    clearAllFilters() {
        this.clearAllFilterGroups();
        this.clearAllFilterButtons();
        this.clearTextFilter();
        this.showAllProducts();
    }

    openItemAccordeon(element) {
        // Open accordeon item if it is closed.
        const accordeonItem = element.closest(".products__accordeon-item");
        accordeonItem.classList.add("products__accordeon-item--open");
    }

    setUpStatusFilter() {
        const filterButtons = this.node.querySelectorAll(".filter__button");
        filterButtons.forEach(item => {
            item.addEventListener("click", (event) => {
                const isOff = item.classList.contains("filter__button--off");
                this.clearAllFilters();
                // Remove off class if exists, otherwise add it
                if (isOff) {
                    item.classList.remove("filter__button--off");
                    const statusIconClass = item.querySelector('svg').classList[1];
                    this.accordeon.querySelectorAll(".products__item").forEach(element => {
                        // If element does not include status icon, make it invisible.
                        if (!element.querySelector(".products__status")) {
                            element.classList.remove("hidden");
                        } else {
                            // If element includes status icon, check if it matches the clicked button.
                            if (element.querySelector(".products__status svg").classList.contains(statusIconClass)) {
                                element.classList.remove("hidden");
                            } else {
                                element.classList.add("hidden");
                            }
                        }
                    });
                } else {
                    item.classList.add("filter__button--off");
                }
            });
        });
    }

    setUpTextFilter() {
        const filterInputs = this.node.querySelectorAll(".filter__input");
        filterInputs.forEach(item => {
            item.addEventListener("keyup", (event) => {
                const text = event.target.value;
                this.clearAllFilters();
                event.target.value = text;
                this.accordeon.querySelectorAll(".products__item").forEach(element => {
                    // If element does not include text, make it invisible.
                    const title = element.innerText.toLowerCase();
                    if (title.includes(text.toLowerCase())) {
                        element.classList.remove("hidden");
                        this.openItemAccordeon(element);
                    } else {
                        element.classList.add("hidden");
                    }
                });
            });
        });
    }

    setUpGroupFilter() {
        const filterCheckboxes = this.node.querySelectorAll(".filter__group--checkbox");

        filterCheckboxes.forEach(checkbox => {
            checkbox.addEventListener("change", (event) => {
                const checkedBoxes = this.node.querySelectorAll(".filter__group--checkbox:checked");
                this.clearAllFilters();

                const checkboxValues = [];
                [...checkedBoxes].forEach(checkbox => {
                    checkbox.checked = true;
                    checkboxValues.push(checkbox.value.toLowerCase());
                });

                this.accordeon.querySelectorAll(".products__item").forEach(element => {
                    const itemGroups = element.querySelector(".products__item-help").innerText.toLowerCase();
                    if (checkboxValues.every(value => itemGroups.includes(value))) {
                        element.classList.remove("hidden");
                        this.openItemAccordeon(element);
                    } else {
                        element.classList.add("hidden");
                    }
                });
            });
        });
    }

    constructor(node) {
        this.node = node;
        this.accordeon = node.parentElement.nextElementSibling;
        this.setUpStatusFilter();
        this.setUpTextFilter();
        this.setUpGroupFilter();
    }
}

[...filterContainers].forEach(filterContainer => new Filter(filterContainer));
