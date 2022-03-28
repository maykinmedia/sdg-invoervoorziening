const forms = document.querySelectorAll('#bevoegde_organisaties_form .form__subforms');


class BevoegdeOrganisatiesForm {

    setUpDynamicCheckbox() {
        // Show field if checkbox is checked
        this.checkbox.addEventListener('change', () => {
            if (this.checkbox.checked) {
                this.formGroup.classList.remove('form__group--hidden');
            } else {
                this.formGroup.classList.add('form__group--hidden');
            }
        });
    }


    constructor(node) {
        this.node = node;
        this.checkbox = this.node.querySelector('[id$="staat_niet_in_de_lijst"]');
        this.nameField = this.node.querySelector('[id$="naam"]');
        this.formGroup = this.nameField.parentElement;
        if (this.nameField.value) {
            this.formGroup.classList.remove('form__group--hidden');
        }
        this.setUpDynamicCheckbox();
    }

}

if (forms) {
    [...forms].forEach(form => new BevoegdeOrganisatiesForm(form));
}

export {BevoegdeOrganisatiesForm};
