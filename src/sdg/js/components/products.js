const productAccordeons = document.querySelectorAll(".products__accordeon");

class Accordeon {
    constructor(node) {
        this.node = node;
        this.items = node.querySelectorAll(".products__accordeon-item");

        [...this.items].forEach(item => {
            item.addEventListener("click", (event) => {
                event.preventDefault();
                const wasOpen = event.currentTarget.classList.contains("products__accordeon-item--open");
                [...this.items].forEach(accordeonItem => accordeonItem.classList.remove("products__accordeon-item--open"));
                if (!wasOpen) {
                    event.currentTarget.classList.add("products__accordeon-item--open");
                }
            });
        });
    }
}

[...productAccordeons].forEach(productAccordeon => new Accordeon(productAccordeon));
