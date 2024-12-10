import { debounce } from "./abstract/utils";
import { Component } from "./abstract/component";

const DYNAMIC_TITLES = document.querySelectorAll(".dynamic_title");
const DEBOUNCE_DELAY = 300;

export class DynamicTitle extends Component {
    /**
     * Constructor method.
     * @param {HTMLElement} node
     */
    constructor(node) {
        super(node);
        this.targetClassname = this.node.dataset.dynamicTitleTarget;
        this.targetElement = this.getDynamicTitleTarget();
    }
    /**
     * Binds events to callbacks.
     * Use this to define EventListeners, MutationObservers etc.
     */
    bindEvents() {
        super.bindEvents();

        this.node.addEventListener(
            "input",
            debounce(this.handleChange.bind(this), DEBOUNCE_DELAY)
        );

        /**
         * Event listener for when the input value is programmatically changed.
         * This must be used in conjunction with node.dispatch(new CustomEvent())
         * to notify that the input value has been updated.
         *
         * @example
         * Dispatching the event:
         * this.node.dispatchEvent(new CustomEvent("forced_input", { detail: { forcedValue: value } }));
         */
        this.node.addEventListener(
            "forced_input",
            this.handleChange.bind(this)
        );
    }

    /**
     * Handles the change event.
     * @param {InputEvent} event
     */
    handleChange(event) {
        const title = event.target.value;
        if (!this.targetElement) return;
        if (!title) this.setValue(""); // Remove dynamic
        else this.setValue(title.trim());
    }

    /**
     * Set the value on the target element.
     * @param {string} value
     */
    setValue(value) {
        this.targetElement.textContent = value;
    }

    /**
     * Get the dynamic title element.
     * @returns {HTMLElement | undefined}
     */
    getDynamicTitleTarget() {
        if (!this.targetClassname) return undefined;

        const titleElement = document.querySelector(this.targetClassname);
        if (!titleElement) return undefined;
        return titleElement;
    }
}

[...DYNAMIC_TITLES].forEach((node) => new DynamicTitle(node));
