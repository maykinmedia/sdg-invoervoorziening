const LANGUAGE_SWITCHES = document.querySelectorAll('.language-switch');

class LanguageSwitch {
    constructor(node) {
        this.node = node;

        if (node) {
            this.bindEvents()
        }
    }

    getStartLanguage() {
        const params = new URLSearchParams(document.location.search);
        const taal = params.get("taal");

        if (taal) {
            return taal
        }

        return "nl"
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

    toggle(active=false) {
        const content = document.querySelector('.content__language-wrapper')

        this.node.classList.toggle('button--active', Boolean(active));

        if (active == true) {
            content.setAttribute("lang", this.node.lang);
        }

        this.changeLanguageContent()
    }

    setStartLanguage(taal="en") {
        const active = this.node.lang === taal;
        this.toggle(active)
    }

    onButtonGroupClick(e) {
        const active = this.node.lang === e.target.lang;
        this.toggle(active)
    }

    bindEvents() {
        this.node.parentElement.addEventListener('click', this.onButtonGroupClick.bind(this));
        this.setStartLanguage(this.getStartLanguage())
    }
}


[...LANGUAGE_SWITCHES].forEach((node) => new LanguageSwitch(node));

