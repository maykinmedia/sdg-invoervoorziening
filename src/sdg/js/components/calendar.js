const inputs = document.querySelectorAll(".calendar");
[...inputs].forEach(input => flatpickr(input, {
    enableTime: true,
}));
