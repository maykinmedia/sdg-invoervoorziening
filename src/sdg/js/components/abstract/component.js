'use strict';


/**
 * Base class for implementing simple components.
 * Provides read-only state machine mutable by setState().
 * Updating state results a render being called.
 * @abstract
 */
export class Component {
    /**
     * Constructor method.
     * @param {HTMLElement} node
     * @param {Object} initialState
     */
    constructor(node, initialState = {}) {
        /** @type {HTMLElement} */
        this.node = node;

        // Protect state methods.
        ['setState', '_setState'].forEach((methodName) =>
            Object.defineProperty(this, methodName, {
                configurable: false,
                value: Component.prototype[methodName].bind(this),
                writable: false
            })
        );

        // Allow other constructor to complete first.
        setTimeout(() => {
            this.setState(initialState);
            this.bindEvents();
        });
    }

    /**
     * Binds events to callbacks.
     * Use this to define EventListeners, MutationObservers etc.
     */
    bindEvents() {
    }

    /**
     * Updates the state with given update.
     * Updating state results a render being called.
     * @param {Object} update partial state with only updated entries.
     * @return {Object} New state.
     */
    setState(update) {
        return this._setState(update);
    }

    /**
     * Renders state.
     * Gets called when state gets updated.
     * Use this to persist (read only) state to DOM.
     * @param {Object} state Read only state.
     */
    render(state) {
    }

    /**
     * Updates the state, this cannot be extended.
     * @param {Object} update partial state with only updated entries.
     * @return {Object} New state.
     */
    _setState(update) {
        // Update state.
        const state = Object.assign(
            Object.assign({}, this.state),  // Clone state.
            update  // Apply update.
        );

        // Mark read only.
        this._markReadOnly(this, 'state', state);

        // Trigger render.
        this.render(this.state);
        return this.state;
    }

    /**
     * Updates key on obj by setting readonly value.
     * @param {obj} obj
     * @param {*} key
     * @param {*} value
     * @return The readonly obj[key].
     * @private
     */
    _markReadOnly(obj, key, value) {
        try {
            obj = Object.defineProperty(obj, key, {
                configurable: true,
                value: value,
                writable: false,
            });
            Object.entries(value).forEach(([nestedKey, nestedValue]) => {
                this._markReadOnly(value, nestedKey, nestedValue);
            });

        } catch (e) {
            console.warn(e);
        }

        return obj[key];
    }
}
