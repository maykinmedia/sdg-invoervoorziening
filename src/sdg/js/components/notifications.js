const notifications = document.querySelectorAll(".notifications__notification");

class Notification {
    constructor(node) {
        this.node = node;
        this.close = node.querySelector(".notifications__close");

        if (this.close) {
            this.close.addEventListener("click", (event) => {
                event.preventDefault();
                this.node.style.opacity = 0;
                setTimeout(() => {
                    this.node.remove();
                }, 300);
            });
        }
    }
}

[...notifications].forEach(notification => new Notification(notification));
