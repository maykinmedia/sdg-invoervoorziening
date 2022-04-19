const LANGUAGE_SWITCHES = document.querySelectorAll('.language-switch');

class LanguageSwitch {
    constructor(node) {
        this.node = node;

        if (node) {
            this.bindEvents()
        }
    }

    changeLanguageContent() {
        const language = document.querySelector('.content__language-wrapper').lang

        document.querySelectorAll('.content__language-wrapper > [lang]').forEach((child) => {
            if (child.hasAttribute('lang')) {
                if (child.lang == language) {
                    child.removeAttribute('aria-hidden')
                } else if (child.lang != language) {
                    child.setAttribute('aria-hidden', true)
                }
            }
        })
    }

    onButtonGroupClick(e) {
        const active = this.node.lang === e.target.lang;
        const content = document.querySelector('.content__language-wrapper')

        this.node.classList.toggle('button--active', Boolean(active));

        if (active == true) {
            content.setAttribute("lang", e.target.lang);
        }

        this.changeLanguageContent()
    }

    bindEvents() {
        this.node.parentElement.addEventListener('click', this.onButtonGroupClick.bind(this));
    }
}


[...LANGUAGE_SWITCHES].forEach((node) => new LanguageSwitch(node));

