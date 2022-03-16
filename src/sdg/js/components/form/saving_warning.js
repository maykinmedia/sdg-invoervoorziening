import {FormComponent} from './abstract/form_component';


/** @type {NodeListOf<HTMLAnchorElement>} */
const WARNING_MESSAGES = document.querySelectorAll('.tabs__table-cell--warning');

/**
 * Button showing diffs between user and stored value of an input.
 */
class SavingWarning extends FormComponent {
    /**
     * Override constructor to add initial values to state.
     * Add listener to input/textarea keyup event.
     */
    bindEvents() {
        super.bindEvents();
        const value = this.getValue();
        const container = this.getFieldContainer();

        this.setState({'initial': value, 'current': value});

        const observer = new MutationObserver(() => {
            this.setState({'current': this.getValue()});
        });
        observer.observe(container, {
            attributes: true,
            childList: true,
            subtree: true
        });
    }

    /**
     * Gets called when this.node gets clicked.
     * @param {MouseEvent} event
     */
    onClick(event) {
        event.preventDefault();
        window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'});
    }

    /**
     * Renders state.
     * Gets called when state gets updated.
     * Use this to persist (read only) state to DOM.
     * @param {Object} state Read only state.
     */
    render(state) {
        const {initial, current} = state;

        if (initial === current) {
            this.node.classList.add('tabs__table-cell--invisible');
        } else {
            this.node.classList.remove('tabs__table-cell--invisible');
        }
    }
}

// Start!
[...WARNING_MESSAGES].forEach((node) => new SavingWarning(node));
