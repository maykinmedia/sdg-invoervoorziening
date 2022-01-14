const expandButtons = document.querySelectorAll(".expand");

class Expand {

    disable() {
        this.node.classList.remove("accent");
        this.open = false;
    }

    enable() {
        this.node.classList.add("accent");
        this.open = true;
    }

    toggle() {
        // Toggle open on if it is true otherwise false.
        this.open ? this.disable() : this.enable();
    }

    constructor(node) {
        this.node = node;
        this.productsContainer = node.closest(".products__catalog").nextElementSibling;
        this.open = false;
        this.node.expander = this;

        this.node.addEventListener("click", (event) => {
            this.productsContainer.querySelectorAll(".products__accordeon-item").forEach(item => {
                if (this.open) {
                    item.classList.remove("products__accordeon-item--open");
                } else {
                    item.classList.add("products__accordeon-item--open");
                }
            });
            this.toggle();
        });
    }
}

[...expandButtons].forEach(expandButton => new Expand(expandButton));
