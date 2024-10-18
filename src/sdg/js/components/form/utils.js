import Diff from "text-diff";
import showdown from "showdown";

/**
 * Global diff html function
 * Returns a string containing html elements of the compared values.
 * @param {string} oldValue - original value.
 * @param {string} newValue - value to compare with - this is also the value that will contain the ins and del elements
 * @returns {string} diffHTML - containing the del and ins elements.
 */
export const returnDiffHTML = (oldValue, newValue) => {
    console.log(oldValue, newValue);
    const diff = new Diff({ timeout: 0, editCost: 4 });
    const textDiff = diff.main(oldValue, newValue);
    diff.cleanupEfficiency(textDiff);
    const prettyHtml = diff
        .prettyHtml(textDiff)
        .replace(/<\/?span[^>]*>/g, "")
        .replace(/<br\/>/g, "\n");
    const diffHTML = new showdown.Converter({ tables: true }).makeHtml(
        prettyHtml
    );
    return diffHTML;
};

export const hideElement = (node) => {
    node.style.display = "none";
    node.setAttribute("aria-hidden", true);
};

export const showElement = (node) => {
    node.removeAttribute("aria-hidden");
    node.style.removeProperty("display");
};
