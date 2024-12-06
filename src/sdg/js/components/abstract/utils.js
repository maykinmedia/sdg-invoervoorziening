/**
 * Removes any text enclosed in parentheses from the input string, including the parentheses themselves,
 * and trims any leading or trailing whitespace from the final result.
 *
 * @param {string} str - The input string from which to remove text within parentheses.
 * @returns {string} - The modified string with all text within parentheses removed.
 */
export function stripParensText(str) {
    // Uses a regular expression to find text within parentheses and remove it.
    // \s* matches any surrounding whitespace.
    // \(.*?\) matches any text within parentheses (non-greedy).
    return str.replace(/\s*\(.*?\)\s*/g, "").trim();
}

/**
 * Creates a debounced function that delays invoking the provided function
 * until after a specified delay has elapsed since the last time it was invoked.
 *
 * @param {Function} func - The function to debounce.
 * @param {number} delay - The number of milliseconds to delay.
 * @returns {Function} - A new debounced function that, when invoked, will
 * delay the execution of the original function by the specified delay time.
 */
export function debounce(func, delay) {
    let inDebounce;
    return function () {
        const context = this;
        const args = arguments;
        clearTimeout(inDebounce);
        inDebounce = setTimeout(() => func.apply(context, args), delay);
    };
}
