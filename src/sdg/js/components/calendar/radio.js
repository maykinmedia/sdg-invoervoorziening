const radioButtons = document.querySelectorAll("input[name=publish]");

class CalendarRadioButton {
    constructor(node) {
        this.node = node;

        node.addEventListener("click", (event) => {
            const container = event.target.parentNode.parentNode.querySelector(".calendar-container");
            if (event.target.value === "later") {
                container.classList.remove("closed");
            } else {
                container.classList.add("closed");
            }
        });
    }
}

[...radioButtons].forEach(radioButton => new CalendarRadioButton(radioButton));
