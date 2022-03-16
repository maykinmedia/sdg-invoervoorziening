import Diff from 'text-diff';
import {ReferenceTextComponent} from './abstract/reference_text_component';


/** @type {NodeListOf<HTMLAnchorElement>} */
const DIFF_BUTTONS = document.querySelectorAll('.form__diff-btn');

/**
 * Button showing diffs between user and stored value of an input.
 */
class DiffButton extends ReferenceTextComponent {
    /**
     * Gets called when this.node gets clicked.
     * @param {MouseEvent} event
     */
    onClick(event) {
        event.preventDefault();
        this.setState({active: !this.state.active, diffHTML: this.getDiffHTML()});
    }

    /**
     * Shows input or textarea.
     */
    showInputOrTextarea() {
        const visibleInputOrTextarea = this.getVisibleInputOrTextarea();
        visibleInputOrTextarea?.style.removeProperty('display');
    }

    /**
     * Hides input or textarea.
     */
    hideInputOrTextarea() {
        const visibleInputOrTextarea = this.getVisibleInputOrTextarea();
        if (visibleInputOrTextarea)
            visibleInputOrTextarea.style.display = 'none';
    }

    /**
     * Shows the diff.
     */
    showDiff() {
        const fieldContainer = this.getFieldContainer();
        const versionsContainer = this.getVersionsContainer();
        const diffElement = fieldContainer.querySelector('.diff');
        versionsContainer.style.removeProperty('display');

        if (diffElement) {
            diffElement.style.removeProperty('display');
        }
    }

    /**
     * Hides the diff.
     */
    hideDiff() {
        const fieldContainer = this.getFieldContainer();
        const versionsContainer = this.getVersionsContainer();
        const diffElement = fieldContainer.querySelector('.diff');
        versionsContainer.style.display = 'none';

        if (diffElement) {
            diffElement.style.display = 'none';
        }
    }

    /**
     * Updates the diff.
     * @return {string} HTML string containing diff.
     */
    getDiffHTML() {
        const previousVersionData = this.getPreviousVersionData();
        const previousValue = previousVersionData.input.value;
        const currentValue = this.getValue();

        const diff = new Diff();
        const textDiff = diff.main(previousValue, currentValue);

        return diff.prettyHtml(textDiff).replace(/\\/g, '');
    }

    /**
     * Renders the diff element.
     * @param {Object} state Read only state.
     */
    renderDiffElement(state) {
        const {diffHTML} = state;

        if (!this.diffElement) {
            const fieldContainer = this.getFieldContainer();
            this.diffElement = document.createElement('div');
            this.diffElement.classList.add('form__input', 'diff');
            fieldContainer.append(this.diffElement);
        }

        this.diffElement.innerHTML = diffHTML;
    }

    /**
     * Renders the diff element.
     */
    renderVersionContainer() {
        const versionsContainer = this.getVersionsContainer();

        if (!versionsContainer.children.length) {
            const previousVersionData = this.getPreviousVersionData();
            const currentVersionData = this.getCurrentVersionData();

            const previousVersionTopElement = document.createElement('del');
            const currentVersionTopElement = document.createElement('ins');

            previousVersionTopElement.innerText = previousVersionData.title;
            currentVersionTopElement.innerText = currentVersionData.title;

            versionsContainer.append(previousVersionTopElement);
            versionsContainer.append(currentVersionTopElement);
        }
    }

    /**
     * Renders state.
     * Gets called when state gets updated.
     * Use this to persist (read only) state to DOM.
     * @param {Object} state Read only state.
     */
    render(state) {
        super.render(state);

        const {active} = state;

        this.renderDiffElement(state);
        this.renderVersionContainer();

        if (active) {
            this.hideInputOrTextarea();
            this.showDiff();
        } else {
            this.showInputOrTextarea();
            this.hideDiff();
        }
    }
}

// Start!
[...DIFF_BUTTONS].forEach((node) => new DiffButton(node));
