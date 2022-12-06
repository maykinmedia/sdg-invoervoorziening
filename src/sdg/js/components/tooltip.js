import {dom} from '@fortawesome/fontawesome-svg-core'
import tippy from "tippy.js";


class InfoTooltip {

    constructor(node) {
        this.node = node;
        const text = this.node.firstChild.textContent;
        if (text) {
            this.node.firstChild.remove();
            tippy(this.node, {
                content: text,
                placement: "right",
                animation: "scale",
                theme: "sdg",
            });
        }
    }
}

const iconsDoneRendering = () => {
    const infoIcons = document.querySelectorAll("svg.fa-circle-info");
    [...infoIcons].forEach(icon => new InfoTooltip(icon));
};

dom.i2svg({callback: iconsDoneRendering});
