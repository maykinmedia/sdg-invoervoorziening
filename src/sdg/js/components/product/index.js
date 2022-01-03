import "./edit";
import "./reference";

// Fill product datetime fields with current date.
document.querySelectorAll('[type="datetime-local"]').forEach(input => {
    input.value = new Date().toISOString().slice(0, -8);
});
