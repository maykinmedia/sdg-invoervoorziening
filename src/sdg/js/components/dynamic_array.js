const arrayWidgets = document.querySelectorAll(".dynamic__container");

let item_count = 1;

function addRemoveEventListener(widgetElement) {
    widgetElement.querySelectorAll('.dynamic__container-remove').forEach(element => {
        element.addEventListener('click', () => {
            element.parentNode.remove();
        });
    });
}

function initializeDynamicWidget(widgetElement) {
    const initialElement = widgetElement.querySelector('.dynamic__container-item');
    const elementTemplate = initialElement.cloneNode(true);
    const parentElement = initialElement.parentElement;

    addRemoveEventListener(widgetElement);

    widgetElement.querySelector('.dynamic__container-add').addEventListener('click', () => {
        item_count++;

        const newElement = elementTemplate.cloneNode(true);

        const id_parts = newElement.querySelector('input').getAttribute('id').split('_');
        const id = id_parts.slice(0, -1).join('_') + '_' + String(item_count - 1);
        newElement.querySelector('input').setAttribute('id', id);
        newElement.querySelectorAll("input").forEach(element => {
            element.value = "";
            ['style', 'data-isnone', 'readonly', 'disabled'].forEach(attribute => element.removeAttribute(attribute));
        });

        addRemoveEventListener(newElement);
        parentElement.appendChild(newElement);
    });
}

[...arrayWidgets].forEach(element => {
    initializeDynamicWidget(element)
});

export {initializeDynamicWidget};
