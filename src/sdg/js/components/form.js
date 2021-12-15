const forms = document.querySelectorAll(".form");

class Form {

    setUpAutomaticDateChange() {
        const calendars = flatpickr(".calendar", {});
        [...calendars].forEach(calendar => {
            calendar.input.addEventListener("change", () => {
                calendars.forEach(c => {
                    c.setDate(calendar.selectedDates[0])
                });
            });
        });
    }

    constructor(node) {
        this.node = node;
        this.setUpAutomaticDateChange();
    }
}

[...forms].forEach(form => new Form(form));
