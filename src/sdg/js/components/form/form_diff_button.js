import Diff from 'text-diff';
import showdown from 'showdown';

import {ReferenceTextComponent} from './abstract/reference_text_component';


/** @type {NodeListOf<HTMLAnchorElement>} */
const DIFF_BUTTONS = document.querySelectorAll('.form__diff-btn');

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
        const currentVersionData = this.getCurrentVersionData();
        let referenceValue = currentVersionData.input.value;
        let ownValue = this.getValue();

        const diff = new Diff({timeout: 0, editCost: 4});
        const textDiff = diff.main(referenceValue, ownValue);
        diff.cleanupEfficiency(textDiff)
        const prettyHtml = diff.prettyHtml(textDiff).replace(/<\/?span[^>]*>/g,"").replace(/<br\/>/g, "\n");
        return new showdown.Converter({tables: true}).makeHtml(prettyHtml)
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
            this.diffElement.classList.add('form__input', 'diff', 'tabs__table-cell', 'tabs__table-cell--value');
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
            const currentVersionData = this.getCurrentVersionData();

            const currentVersionTopElement = document.createElement('ins');
            const previousVersionTopElement = document.createElement('del');

            currentVersionTopElement.innerText = "Mijn tekst";
            previousVersionTopElement.innerText = currentVersionData.title;

            versionsContainer.append(currentVersionTopElement);
            versionsContainer.append(previousVersionTopElement);
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
[...DIFF_BUTTONS].forEach((node) => new FormDiffButton(node));
