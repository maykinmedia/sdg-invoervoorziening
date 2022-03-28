import toArray from 'arrayify';
import BEM from 'bem.js';
import {initializeDynamicWidget} from './dynamic_array';
import Choices from 'choices.js'
import {CHOICES_CONFIG} from './choices';
import {BevoegdeOrganisatiesForm} from "./bevoegde_organisaties";


const BLOCK_FORMSET = 'formset';
const DYNAMIC = 'dynamic';

const ELEMENT_BODY = 'body';
const ELEMENT_TEMPLATE = 'template';
const ELEMENT_ADD = 'add';
const ELEMENT_REMOVE = 'remove';
const ELEMENT_TITLE = 'title';
const ELEMENT_CONTAINER = 'container';

const FORMSET = BEM.getBEMNode(BLOCK_FORMSET);
const FORMSET_BODY = BEM.getBEMNode(BLOCK_FORMSET, ELEMENT_BODY);
const TEMPLATE = BEM.getBEMNode(BLOCK_FORMSET, ELEMENT_TEMPLATE);
const ADD = BEM.getBEMNode(BLOCK_FORMSET, ELEMENT_ADD);

const MATCH_FORM_IDS = /(id|for|name)="(.+?)"/g;
const PREFIX_PLACEHOLDER = '__prefix__';


/**
 * Formset class
 * Contains logic for the add member form
 * @class
 */
class Formset {
    /**
     * Constructor method
     * Gets called when class get instantiated
     */
    constructor() {
        if (ADD) {
            this.setUpAddForm();
            this.setUpRemoveForm();
        }
    }

    /**
     * Binds ADD click to this.addForm()
     */
    setUpAddForm() {
        ADD.addEventListener('click', (e) => {
            e.preventDefault();
            this.addForm();
        });
    }

    /**
     * Binds REMOVE click to this.removeForm()
     */
    setUpRemoveForm() {
        toArray(FORMSET_BODY.children).forEach(el => {
            this.setUpRemoveFormForElement(el)
        });
    }

    /**
     * Binds REMOVE click to this.removeForm()
     */
    setUpRemoveFormForElement(el) {
        const removeButton = BEM.getChildBEMNode(el, BLOCK_FORMSET, ELEMENT_REMOVE);
        removeButton.addEventListener('click', (e) => {
            e.preventDefault();
            this.removeForm(e);
        });
    }

    /**
     * Creates a new form based on TEMPLATE
     * Updates the id's of the form to unique values
     * Applies styling to fake elements (checkboxes, radio buttons, datepicker)
     */
    addForm() {
        // Creates a new form based on TEMPLATE
        let template = document.importNode(TEMPLATE.content, true);

        FORMSET_BODY.appendChild(template);
        let form = FORMSET_BODY.children[FORMSET_BODY.children.length - 1];

        // Updates the id's of the form to unique values
        form.innerHTML = form.innerHTML.replace(MATCH_FORM_IDS, this.updateMatchedId.bind(this, form));
        const formsetTitle = BEM.getChildBEMNode(form, BLOCK_FORMSET, ELEMENT_TITLE);
        formsetTitle.innerHTML = formsetTitle.innerHTML.replace(
            PREFIX_PLACEHOLDER, this.getFormIndex.bind(this, form)() + 1
        );

        let index = FORMSET_BODY.children.length;
        FORMSET.querySelector('[name="form-TOTAL_FORMS"]').value = index;
        this.setUpRemoveFormForElement(form);

        // TODO: Refactor below this line (re-adding listeners to any dynamic elements)
        const dynamicElements = BEM.getChildBEMNodes(form, DYNAMIC, ELEMENT_CONTAINER);
        if (dynamicElements) {
            [...dynamicElements].forEach(element => {
                initializeDynamicWidget(element)
            });
        }

        const choiceElements = form.querySelectorAll('.choices');
        [...choiceElements].forEach(element => { new Choices(element, CHOICES_CONFIG)});

        if (form.closest('#bevoegde_organisaties_form')) {
            new BevoegdeOrganisatiesForm(form);
        }
    }

    getFormIndex(form) {
        return toArray(FORMSET_BODY.children).indexOf(form);
    }

    /**
     * Callback function for replacing ids in form
     * Replaces PREFIX_PLACEHOLDER with index of form
     * @param {HTMLFormElement} form The form we're replacing id's for
     * @param {string} match The string matching MATCH_FORM_IDS
     * @param {string} attr (Capturing group) the matched attribute
     * @param {string} id (Capturing group) the value of the attr
     * @returns {string} An html attribute/value pair with PREFIX_PLACEHOLDER replaced
     */
    updateMatchedId(form, match, attr, id) {  // jshint unused:false
        const index = this.getFormIndex(form);
        id = id.replace(PREFIX_PLACEHOLDER, index);
        return `${attr}="${id}"`;
    }

    /**
     * Removes the selected form
     */
    removeForm(e) {
        const form = e.target.parentNode.parentNode;
        form.classList.add("hidden");
        form.querySelector(`[name="form-${this.getFormIndex(form)}-DELETE"]`).checked = true;
    }
}

new Formset();
