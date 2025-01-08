import { ReferenceTextComponent } from "./abstract/reference_text_component";
import { hideElement, returnDiffHTML, showElement } from "./utils";

/** @type {NodeListOf<HTMLButtonElement>} */
const DIFF_BUTTONS = document.querySelectorAll(".form__diff-btn");

/**
 * Button showing diffs between user and stored value of an input.
 */
class FormDiffButton extends ReferenceTextComponent {
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
        const currentVersionData = this.getCurrentVersionData();

        return Object.entries(currentVersionData).reduce(
            (acc, [language, { input }]) => {
                const values = this.getValues();
                const currentVersionValue = input.value;
                const currentValue = values[language];
                acc[language] = returnDiffHTML(
                    currentVersionValue,
                    currentValue
                );
                return acc;
            },
            {}
        );
    }

    /**
     * Shows input or textarea.
     */
    showInputOrTextarea() {
        Object.values(this.getVisibleInputOrTextareas()).forEach(showElement);
    }

    /**
     * Hides input or textarea.
     */
    hideInputOrTextarea() {
        Object.values(this.getVisibleInputOrTextareas()).forEach(hideElement);
    }

    /**
     * Shows the diff.
     */
    showDiff() {
        Object.values(this.getDiffElements()).forEach(showElement);
    }

    /**
     * Hides the diff.
     */
    hideDiff() {
        Object.values(this.getDiffElements()).forEach(hideElement);
    }

    /**
     * Render diffHTMl into the preview element
     * @param {{ [language: string]: string } | undefined} diffHTML
     */
    renderDiffPreview(diffHTML) {
        if (!diffHTML) return;
        Object.entries(this.getDiffPreviewElements()).forEach(
            ([language, node]) => (node.innerHTML = diffHTML[language])
        );
    }

    /**
     * Render the diff versions into the versions element
     * @param {{ [language: string]: string } | undefined} diffHTML
     */
    renderDiffVersions() {
        Object.entries(this.getDiffVersionElements()).forEach(
            ([language, node]) => {
                const currentVersionData = this.getCurrentVersionData();
                node.querySelector("ins").innerText = "Mijn text";
                node.querySelector("del").innerText =
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

        this.renderDiffVersions();

        if (active) {
            this.renderDiffPreview(diffHTML);
            this.hideInputOrTextarea();
            this.showDiff();
        } else {
            this.showInputOrTextarea();
            this.hideDiff();
        }
    }
}

// Start!
[...DIFF_BUTTONS].forEach((node) => new FormDiffButton(node));
