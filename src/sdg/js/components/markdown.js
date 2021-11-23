import ClassicEditor from './ckeditor';

function applyMarkdownEditors(selector) {
    const markdownFields = document.querySelectorAll(selector);
    const availableEditors = {};

    [...markdownFields].forEach(field => {
        ClassicEditor.create(field).then(editor => {
            availableEditors[field.id] = editor;
            editor.isReadOnly = field.readOnly;
        });
    });

    return availableEditors;
}

const availableEditors = applyMarkdownEditors(".markdownx textarea");

export {availableEditors};
