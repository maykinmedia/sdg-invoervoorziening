import tippy from "tippy.js";

const infoIcons = document.querySelectorAll("svg.fa-info-circle[title]");

class InfoTooltip {

    constructor(node) {
        this.node = node;
        tippy(this.node, {
            content: this.node.firstChild.textContent,
            placement: "right",
            animation: "scale",
            theme: "sdg",
        });
    }
}

document.addEventListener("DOMContentLoaded", () => {
    [...infoIcons].forEach(icon => new InfoTooltip(icon));
});

