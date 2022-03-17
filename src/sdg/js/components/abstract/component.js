'use strict';


/**
 * Base class for implementing simple components.
 * Provides read-only state machine mutable by setState().
 * Updating state results in a render being called.
 *
 * Please see options for list of available options.
 * @abstract
 */
export class Component {
    /**
     * Default state object.
     * Use this to specify the default state of the component.
     * @type {Object}
     */
    static initialState = {};

    /**
     * Options object.
     * Use this to specify the options of the component.
     *
     * Options:
     *  - observe {boolean} Use a MutationObserver to track, and react on changes to this.node in DOM.
     *
     * @type {Object}
     */
    static options = {};

    /**
     * Constructor method.
     * @param {HTMLElement} node
     * @param {Object} initialState
     * @param {Object} options
     */
    constructor(
        node,
        initialState = this.constructor.initialState,
        options = this.constructor.options
    ) {
        /** @type {HTMLElement} */
        this.node = node;

        /** @type {boolean} Whether the `this.node` is considered to be mounted (attached to DOM). */
        this._isMounted = false;

        /** @type {Object} */
        this._options = this._getOptions(options);

        /** @type {(MutationObserver|null)} */
        this._mutationObserver = this._options.observe ? this._getMutationObserver() : null;


        /** @type {Object} */
        this.state = {};

        // Protect state methods.
        ['setState', '_setState', '_bindEvents'].forEach((methodName) =>
            Object.defineProperty(this, methodName, {
                configurable: false,
                value: Component.prototype[methodName].bind(this),
                writable: false
            })
        );

        // Mark read only.
        this._markReadOnly(this, '_options', this._options);
        this._markReadOnly(this, 'state', this.state);

        if (this._options.observe) {
            this._markReadOnly(this, 'mutationObserver', this._mutationObserver);
        }

        this._setState(initialState);
        this._bindEvents();
    }

    /**
     * Gets called after the first render cycle.
     * Use this to sync state with DOM on initial mount.
     */
    onMount() {
    }

    /**
     * Gets called when MutationObservers detects a mutation.
     * Only when `options.observe` is set to `true`.
     * Use this to sync state with DOM updates.
     * @param {MutationRecord} mutationRecord
     */
    onMutation(mutationRecord) {
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
     * (Re)connects the MutationObserver.
     * requires `options.observe` to be `true`.
     */
    connectObserver() {
        if (!this._options.observe) {
            throw new Error(`Cannot connect uninitialized MutationObserver on ${this.node}, please use options.observe.`);
        }

        // Postpone re-observation to the end of the event loop.
        setTimeout(() => {
            this._mutationObserver?.observe(this.node, {
                attributes: true,
                childList: true,
                subtree: true,
                attributeOldValue: true,
            });
        });
    }

    /**
     * Disconnects the MutationObserver.
     * requires `options.observe` to be `true`.
     */
    disconnectObserver() {
        if (!this._options.observe) {
            throw new Error(`Cannot disconnect uninitialized MutationObserver on ${this.node}, please use options.observe.`);
        }
        this._mutationObserver?.disconnect();
    }

    /**
     * Returns the combined options.
     * @param {Object} options
     * @return {Object}
     * @private
     */
    _getOptions(options) {
        const defaults = {
            observe: false,
        }
        return Object.assign(defaults, options);
    }

    /**
     * Binds events to callbacks.
     */
    _bindEvents() {
        if (this._options.observe) {
            this.connectObserver();
        }

        // Allow component implementation to construct first.
        // This allows `this.bindEvens()` to use attributes specified implementation's constructor.
        setTimeout(this.bindEvents.bind(this));
    }

    /**
     * Returns a MutationObserver observing changes to this.node.
     * Changes to this.node result in render.
     * @return {MutationObserver}
     * @private
     */
    _getMutationObserver() {
        if (!this._options.observe) {
            throw new Error(`Cannot create MutationObserver on ${this.node}, please use options.observe.`);
        }

        return new MutationObserver(this._onMutation.bind(this));
    }

    /**
     * Gets called when MutationObservers detects a mutation.
     * Only when `options.observe` is set to `true`.
     * @param {MutationRecord[]} mutationRecords
     * @param {MutationObserver} mutationObserver
     */
    _onMutation(mutationRecords, mutationObserver) {
        [...mutationRecords].forEach((mutationRecord) => {
            this.onMutation(mutationRecord);
        });
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
        setTimeout(() => {
            this._render(this.state);
        })
        return this.state;
    }

    /**
     * Updates key on obj by setting readonly value.
     * @param {Object} obj
     * @param {*} key
     * @param {*} value
     * @return The readonly obj[key].
     * @private
     */
    _markReadOnly(obj, key, value) {
        obj = Object.defineProperty(obj, key, {
            configurable: true,
            value: value,
            writable: false,
        });

        if (typeof value === 'object' && value !== null) {
            Object.entries(value).forEach(([nestedKey, nestedValue]) => {
                this._markReadOnly(value, nestedKey, nestedValue);
            });
        }

        return obj[key];
    }

    /**
     * Renders state.
     * Gets called when state gets updated.
     * Disconnects this._mutationObserver temporary while allow this.render() to execute.
     * This prevents infinite loops while rendering.
     * @param {Object} state Read only state.
     */
    _render(state) {
        if (this._options.observe) {
            this.disconnectObserver();
        }

        this.render(state);

        if (this._options.observe) {
            this.connectObserver();
        }

        if (!this._isMounted && this.node.isConnected) {
            this._isMounted = true;
            this.onMount();
        }
    }
}
