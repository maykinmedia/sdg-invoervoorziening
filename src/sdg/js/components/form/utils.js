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

/**
 * Get an url that can be used to fetch data from the CMS API using a given URLSearchParams.
 * @param {Record<string, string>} searchParams
 * @returns {URL}
 * @todo Convert this part to an API class, if the front-end requests the CMS API on more places.
 */
export function getCmsApiTranslationURL(searchParams) {
    const url = new URL(
        `${SubPath}/cmsapi/translation/`,
        window.location.origin
    );
    if (!searchParams) return url;

    url.search = new URLSearchParams(searchParams);
    return url;
}

/**
 * Perform a fetch to the
 * @param {string} productId
 * @returns {Promise<{[language: string], string}>}
 */
export async function fetchCmsApiProductTranslationName(productId) {
    const url = getCmsApiTranslationURL({ product_id: productId });

    const jsonToTitle = (result) => {
        return result.productTitel
            ? result.productTitel
            : result.generiekProduct;
    };

    try {
        return await fetch(url.toString())
            .then((response) => response.json())
            .then((data) => data.results)
            .then((results) => {
                return results.reduce((acc, result) => {
                    acc[result.taal] = jsonToTitle(result);
                    return acc;
                }, {});
            });
    } catch (error) {
        return {};
    }
}
