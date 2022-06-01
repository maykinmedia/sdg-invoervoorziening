import Diff from 'text-diff';
import showdown from 'showdown';

import {ReferenceTextComponent} from './abstract/reference_text_component';


/** @type {NodeListOf<HTMLAnchorElement>} */
const DIFF_BUTTONS = document.querySelectorAll('.reference__diff-btn');

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
        this.setState({active: !this.state.active, diffHTML: this.getDiffHTML()});
    }

    /**
     * Updates the diff.
     * @return {string} HTML string containing diff.
     */
    getDiffHTML() {
        const previousVersionData = this.getPreviousVersionData();
        const previousVersionValue = previousVersionData.input.value;
        const currentVersionData = this.getCurrentVersionData();
        const currentVersionValue = currentVersionData.input.value;

        const diff = new Diff({timeout: 0, editCost: 4});
        const textDiff = diff.main(previousVersionValue, currentVersionValue);
        diff.cleanupEfficiency(textDiff)
        const prettyHtml =  diff.prettyHtml(textDiff).replace(/<\/?span[^>]*>/g,"").replace(/<br\/>/g, "\n");
        return new showdown.Converter({tables: true}).makeHtml(prettyHtml);
    }

    /**
     * Renders the diff element.
     */
    renderVersionContainer() {
        const referenceTextContainer = this.getReferenceTextContainer().parentElement;
        const versionsContainer = document.createElement('div');
        versionsContainer.classList.add('tabs__table-cell--versions');
        referenceTextContainer.prepend(versionsContainer);

        const previousVersionData = this.getPreviousVersionData();
        const currentVersionData = this.getCurrentVersionData();

        const previousVersionTopElement = document.createElement('del');
        const currentVersionTopElement = document.createElement('ins');

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
    render(state) {
        super.render(state);
        const {active, diffHTML} = state;

        const referenceTextContainer = this.getReferenceTextContainer();

        if(active) {
            referenceTextContainer.innerHTML = diffHTML;
            this.renderVersionContainer();
        } else {
            referenceTextContainer.innerHTML = this.getReferenceHTML();
            const version = referenceTextContainer.parentNode.getElementsByClassName("tabs__table-cell--versions")
            if (version !== undefined && version.length > 0) {
                referenceTextContainer.parentNode.removeChild(version[0])
            }
        }
    }
}

// Start!
[...DIFF_BUTTONS].forEach((node) => new ReferenceDiffButton(node));
