const language_toolboxes = document.querySelectorAll('.toolbox__language_div');

class LanguageToolboxToggle {
    /**
     * Constructor method.
     * @param {HTMLFormElement} node
     */
    constructor(node) {
        this.node = node;

        if (this.node) {
            if (this.getLanguage()) {
                this.toggle();
            }
        }
    }

    toggle() {
        this.getLanguage().addEventListener("change", (event) => {
            activeLang = this.getLanguage().checked ? 'en' : 'nl'

            let items = this.node.querySelectorAll('.toolbox__language_item')

            items.forEach((item) => {
                if (item.lang === activeLang) {
                    item.removeAttribute('aria-hidden')
                } else {
                    item.setAttribute('aria-hidden', true);
                }
            });
        })
    }

    getLanguage() {
        try {
            const globalSwitch = document.querySelector('.global-language-switch');
            return globalSwitch.querySelector('.toggle input[type=checkbox]');
        } catch (e) {
            return null;
        }
    }
}

if (language_toolboxes) {
    [...language_toolboxes].forEach((node) => new LanguageToolboxToggle(node));
}
