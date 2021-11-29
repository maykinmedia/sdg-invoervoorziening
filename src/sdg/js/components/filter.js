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
        this.showAllProducts();
    }

    clearAllFilterButtons() {
        // Clear all filter buttons
        const filterButtons = this.node.querySelectorAll(".filter__button");
        filterButtons.forEach(item => {
            item.classList.add("filter__button--off");
        });
        this.showAllProducts();
    }

    setUpStatusFilter() {
        const filterButtons = this.node.querySelectorAll(".filter__button");
        filterButtons.forEach(item => {
            item.addEventListener("click", (event) => {
                const isOff = item.classList.contains("filter__button--off");
                this.clearAllFilterButtons();
                this.clearTextFilter();
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
                this.clearAllFilterButtons();
                this.accordeon.querySelectorAll(".products__item").forEach(element => {
                    // If element does not include text, make it invisible.
                    if (element.innerText.toLowerCase().includes(event.target.value.toLowerCase())) {
                        element.classList.remove("hidden");
                        const accordeonItem = element.closest(".products__accordeon-item");
                        // Open accordeon item if it is closed.
                        accordeonItem.classList.add("products__accordeon-item--open");
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
    }
}

[...filterContainers].forEach(filterContainer => new Filter(filterContainer));
