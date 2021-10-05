import ClassicEditor from './ckeditor';

export default function applyMarkdownEditors (selector) {
    const markdownFields = document.querySelectorAll(selector);
    const availableEditors = {};

    [...markdownFields].forEach(field => {
         ClassicEditor.create(field).then(editor => {
            availableEditors[field.id] = editor
        });
    });

    return availableEditors;
}
