const markdownFields = document.querySelectorAll(".markdownx textarea");

mdeObject = {};

[...markdownFields].forEach(field => {
    mdeObject[field.id] = new SimpleMDE({
        element: field,
        autoDownloadFontAwesome: false,
        spellChecker: false,
    });
});
