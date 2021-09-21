const notifications = document.querySelectorAll(".notifications__notification");

class Notification {
    constructor(node) {
        this.node = node;
        this.close = node.querySelector(".notifications__close");

        this.close.addEventListener("click", () => {
            this.node.remove()
        });
    }
}

[...notifications].forEach(notification => new Notification(notification));
