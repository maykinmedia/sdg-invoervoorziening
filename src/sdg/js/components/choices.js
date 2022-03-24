import Choices from 'choices.js'

export const CHOICES_CONFIG = {
        loadingText: 'Laden...',
        noResultsText: 'Geen resultaten gevonden',
        noChoicesText: 'Geen keuzes om uit te kiezen',
        itemSelectText: 'Druk om te kiezen',
    };

const fields = document.querySelectorAll(".choices");
[...fields].forEach(element => new Choices(element, CHOICES_CONFIG));
