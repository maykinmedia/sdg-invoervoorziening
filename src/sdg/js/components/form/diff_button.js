import Diff from 'text-diff';
import {FormComponent} from './abstract/form_component';


/** @type {NodeListOf<HTMLAnchorElement>} */
const DIFF_BUTTONS = document.querySelectorAll('.form__diff-btn');


/**
 * Button showing diffs between user and stored value of an input.
 */
class DiffButton extends FormComponent {
    /**
     * Gets called when this.node gets clicked.
     * @param {MouseEvent} event
     */
    onClick(event) {
        event.preventDefault();
        this.setState({active: !this.state.active});
    }

    /**
     * Shows input or textarea.
     */
    showInputOrTextarea() {
        const visibleInputOrTextarea = this.getVisibleInputOrTextarea();
        visibleInputOrTextarea.style.removeProperty('display');
    }

    /**
     * Hides input or textarea.
     */
    hideInputOrTextarea() {
        const visibleInputOrTextarea = this.getVisibleInputOrTextarea();
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
     */
    updateDiff() {
        const currentVersionData = this.getCurrentVersionData();
        const previousVersionData = this.getPreviousVersionData();
        const fieldContainer = this.getFieldContainer();
        const currentDiffElement = fieldContainer.querySelector('.diff');
        const versionsContainer = this.getVersionsContainer();
        const previousValue = previousVersionData.input.value;
        const currentValue = this.getValue();

        const diff = new Diff();
        const textDiff = diff.main(previousValue, currentValue);
        const diffElement = document.createElement('div');

        diffElement.classList.add('form__input', 'diff');
        diffElement.innerHTML = diff.prettyHtml(textDiff).replace(/\\/g, '');

        if (currentDiffElement) {
            fieldContainer.removeChild(currentDiffElement);
        }

        fieldContainer.append(diffElement);

        const previousVersionTopElement = document.createElement('del');
        const currentVersionTopElement = document.createElement('ins');

        while (versionsContainer.firstChild) {
            versionsContainer.removeChild(versionsContainer.firstChild);
        }

        previousVersionTopElement.innerText = previousVersionData.title;
        currentVersionTopElement.innerText = currentVersionData.title;

        versionsContainer.append(previousVersionTopElement);
        versionsContainer.append(currentVersionTopElement);
    }

    /**
     * Renders state.
     * Gets called when state gets updated.
     * Use this to persist (read only) state to DOM.
     * @param {Object} state Read only state.
     */
    render({active}) {
        this.node.classList.toggle('button--active', Boolean(active));
        this.updateDiff();

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
