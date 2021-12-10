import flatpickr from "flatpickr";

const inputs = document.querySelectorAll(".calendar");
[...inputs].forEach(input => flatpickr(input, {
    defaultDate: input.value || new Date(),
}));
