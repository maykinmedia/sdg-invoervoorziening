import { ReferenceTextComponent } from "./abstract/reference_text_component";
import { hideElement, returnDiffHTML, showElement } from "./utils";

/** @type {NodeListOf<HTMLAnchorElement>} */
const DIFF_BUTTONS = document.querySelectorAll(".reference__diff-btn");

/**
 * Button showing diffs between reference and previous reference.
 */
class ReferenceDiffButton extends ReferenceTextComponent {
    /**
     * Gets called when this.node gets clicked.
     * @param {MouseEvent} event
     */
    onClick(event) {
        event.preventDefault();
        this.setState({
            active: !this.state.active,
            diffHTML: this.getDiffHTML(),
        });
    }

    /**
     * Get the diff HTML containing ins and del elements.
     * @return {{ [language: string]: string }} Object with each key as a language and a property of the string containing the diff.
     */
    getDiffHTML() {
        const previousVersionData = this.getPreviousVersionData();
        const currentVersionData = this.getCurrentVersionData();

        return Object.entries(previousVersionData).reduce(
            (acc, [language, { input }]) => {
                const previousVersionValue = input.value;
                const currentVersionValue =
                    currentVersionData[language].input.value;

                acc[language] = returnDiffHTML(
                    previousVersionValue,
                    currentVersionValue
                );
                return acc;
            },
            {}
        );
    }

    /**
     * Shows the reference version containers
     */
    showReferenceVerions() {
        Object.values(this.getReferenceVersionElements()).forEach(showElement);
    }

    /**
     * Hides the reference version containers
     */
    hideReferenceVerions() {
        Object.values(this.getReferenceVersionElements()).forEach(hideElement);
    }

    /**
     * Render diffHTMl into the preview element
     * @param {{ [language: string]: string } | undefined} diffHTML
     */
    renderReferencePreview(diffHTML) {
        if (!diffHTML) return;
        Object.entries(this.getReferencePreviewElements()).forEach(
            ([language, node]) => {
                if (diffHTML[language]) node.innerHTML = diffHTML[language];
            }
        );
    }

    /**
     * Renders the reference version elements.
     */
    renderReferenceVersions() {
        Object.entries(this.getReferenceVersionElements()).forEach(
            ([language, node]) => {
                const previousVersionData = this.getPreviousVersionData();
                const currentVersionData = this.getCurrentVersionData();
                node.querySelector("del").innerText =
                    previousVersionData[language].title;
                node.querySelector("ins").innerText =
                    currentVersionData[language].title;
            }
        );
    }

    /**
     * Renders state.
     * Gets called when state gets updated.
     * Use this to persist (read only) state to DOM.
     * @param {Object} state Read only state.
     */
    render(state) {
        super.render(state);
        const { active, diffHTML } = state;

        this.renderReferenceVersions();

        if (active) {
            this.renderReferencePreview(diffHTML);
            this.showReferenceVerions();
        } else {
            this.createCurrentReferences();
            this.hideReferenceVerions();
        }
    }
}

// Start!
[...DIFF_BUTTONS].forEach((node) => new ReferenceDiffButton(node));
