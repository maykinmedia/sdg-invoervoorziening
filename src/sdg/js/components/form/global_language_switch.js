import {LanguageSwitch} from './language_switch';

/** @type {NodeListOf<HTMLButtonElement>} */
const GLOBAL_LANGUAGE_SWITCHES = document.querySelectorAll('.global-language-switch');

/**
 * Sets the language of all form controls.
 */
class GlobalLanguageSwitch extends LanguageSwitch {

    /**
     * Returns whether this language switch is global.
     */
    isGlobal() {
        return true;
    }

    /**
     * Returns the active form control.
     * @return {(HTMLElement|null)}
     */
    getFormControl() {
        return null;
    }

    /**
     * Returns the icon.
     * @return {SVGSVGElement}
     */
    getIcon() {
        return null;
    }

    /**
     * Returns all the language wrappers.
     * @return {HTMLElement}
     */
    getLanguageWrappers() {
        return document.querySelectorAll('.form__language-wrapper');
    }


    /**
     * Returns the language of this button.
     * @return {string}
     */
    getLanguage() {
        return this.node.querySelector('.toggle input[type=checkbox]').checked ? 'en' : 'nl';
    }
}

// Start!
[...GLOBAL_LANGUAGE_SWITCHES].forEach((node) => new GlobalLanguageSwitch(node));
