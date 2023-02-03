const form = document.querySelector('.form');

class GenericForm {
    /**
     * Constructor method.
     * @param {HTMLFormElement} node
     */
    constructor(node) {
        /** @type {HTMLFormElement} */
        this.node = node;

        if(!this.isGenericForm()) {
            return;  // Not a generic form.
        }

        if (this.node) {
            this.disableButtons();
        }
    }

    /**
     * Returns whether `this.node` represents a generic form based on node tree.
     * @return {boolean}
     */
    isGenericForm() {
        return Boolean(this.getPublishButton(), this.getConceptButton());
    }

    /**
     * Returns button (if found).
     * @return {(Element|null)}
    */
    getPublishButton() {
        return this.node.querySelector('[id$="publish-button"]');
    }

    /**
     * Returns button (if found).
     * @return {(Element|null)}
    */
    getConceptButton() {
        return this.node.querySelector('[id$="concept-button"]');
    }


    disableButtons() {
        const concept = this.getConceptButton()
        const publish = this.getPublishButton()

        if (concept && publish) {           
            let executed = false;

            const disableFunc = (event) => {
                if (this.node.checkValidity()) {

                    if (executed) {
                        event.preventDefault();
                    }
                    executed = true;
                }
            };

            concept.addEventListener("click", disableFunc);
            publish.addEventListener("click", disableFunc);
        };
    }

}

if (form) {
    new GenericForm(form);
}
