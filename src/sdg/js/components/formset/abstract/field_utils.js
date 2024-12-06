/**
 * Simple class for implementing field components (`input[type='text']`) within the formset form component.
 * @abstract
 */
export class TextField {
    /**
     * Construct the NumberField
     * @param {HTMLInputElement} node
     */
    constructor(node) {
        this.node = node;

        /** @type {string} */
        this.value = node.value;
    }

    /**
     * Set the value of the totalForms field
     * @param {string} value
     */
    setValue(value) {
        this.node.value = value;
    }
}

/**
 * Simple class for implementing field components (`input[type='number']`) within the formset form component.
 * @abstract
 */
export class NumberField {
    /**
     * Construct the NumberField
     * @param {HTMLInputElement} node
     */
    constructor(node) {
        this.node = node;

        /** @type {number} */
        this.value = parseInt(node.value);
    }

    /**
     * Set the value of the totalForms field
     * @param {number} value
     */
    setValue(value) {
        this.node.value = value;
    }
}

/**
 * Simple class for implementing field components (`input[type='checkbox']`) within the formset form component.
 * @abstract
 */
export class CheckboxField {
    /**
     * Construct the CheckboxField
     * @param {HTMLInputElement} node
     */
    constructor(node) {
        this.node = node;

        /** @type {boolean} */
        this.checked = parseInt(node.checked);
    }

    /**
     * Set the checked value
     * @param {boolean} checked
     */
    setChecked(checked) {
        this.node.checked = checked;
    }
}
