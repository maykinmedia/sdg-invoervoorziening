const expandButtons = document.querySelectorAll(".expand");

class Expand {
    constructor(node) {
        this.node = node;
        this.productsContainer = node.closest(".products__catalog").nextElementSibling;
        this.expand = true;

        this.node.addEventListener("click", (event) => {
            this.expand ? this.node.classList.add("accent") : this.node.classList.remove("accent");
            this.productsContainer.querySelectorAll(".products__accordeon-item").forEach(item => {
                if (this.expand) {
                    item.classList.add("products__accordeon-item--open");
                } else {
                    item.classList.remove("products__accordeon-item--open");
                }
            });
            // Toggle expand on if it is true otherwise false.
            this.expand = !this.expand;
        });
    }
}

[...expandButtons].forEach(expandButton => new Expand(expandButton));
