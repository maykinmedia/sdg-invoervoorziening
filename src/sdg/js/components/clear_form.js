import {availableEditors} from './markdown'
const form = document.querySelector('.form');

class ClearForm {
    constructor(node) {
        this.node = node;


        if (this.node) {
            this.clearFormAanwezig()
            this.clearFormValtOnder()
        }
    }

    resetSpecefiekeGegevens() {
        const none_markdown_editor_fields = [
            "[name=vertalingen-0-product_titel_decentraal]",
            "[name=vertalingen-1-product_titel_decentraal]",
            "[name=vertalingen-0-decentrale_procedure_link]",
            "[name=vertalingen-1-decentrale_procedure_link]",
            "[name=vertalingen-0-decentrale_procedure_label]",
            "[name=vertalingen-1-decentrale_procedure_label]"
        ]
        const array_fields = [
            "[name=vertalingen-0-verwijzing_links]",
            "[name=vertalingen-1-verwijzing_links]",
        ]
        const markdown_editor_fields = document.querySelectorAll('.markdownx textarea');

        none_markdown_editor_fields.forEach((field) => {
            let input_field = this.node.querySelector(field);
            if (input_field) {
                input_field.value = ''
            }
        })

        array_fields.forEach((field) => {
            let input_fields = this.node.querySelectorAll(field);
            input_fields.forEach((input_field) => {
                if (input_field) {
                    input_field.value = ''
                }
            })
        })

        markdown_editor_fields.forEach((field) => {
            field.value = ''
        })

        Object.values(availableEditors).forEach((instance) => {
            instance.editor.setData("")
        })
    }

    clearFormAanwezig() {
        const input = this.node.querySelector("[name=product_aanwezig]");

        if (input) {
            let prev = input.selectedIndex;
            const clearFunc = () => {
                if (input.selectedIndex === 2) {
                    if (confirm("Weet u zeker dat u dit product niet aanbiedt?\nAls u 'Ja' antwoord worden alle teksten leeggemaakt.")) {
                        this.resetSpecefiekeGegevens();
                    } else {
                        input.selectedIndex = prev;
                    }
                }

                prev = input.selectedIndex;
            }

            input.addEventListener("change", (event) => {
                clearFunc();
            });
        }
    }

    clearFormValtOnder() {
        const input = this.node.querySelector("[name=product_valt_onder]");

        if (input) {
            let prev = input.selectedIndex;
            const clearFunc = () => {
                if (input.selectedIndex > 0) {
                    if (confirm("Weet u zeker dat u dit product niet aanbiedt?\nAls u 'OK' antwoord worden alle teksten leeggemaakt.")) {
                        this.resetSpecefiekeGegevens();
                    } else {
                        input.selectedIndex = prev;
                    }
                }

                prev = input.selectedIndex;
            }

            input.addEventListener("change", () => {
                clearFunc();
            });
        }
    }
}

if (form) {
    new ClearForm(form);
}
