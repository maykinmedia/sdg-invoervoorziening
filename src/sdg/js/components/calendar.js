const inputs = document.querySelectorAll(".calendar");
[...inputs].forEach(input => flatpickr(input, {
    enableTime: true,
    time_24hr: true,
}));
