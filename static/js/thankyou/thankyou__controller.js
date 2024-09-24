import { navigationLeftToHomePage } from "../utils/navigationLeftToHomePage.js"
import { getUserDomElements, setupEventListeners } from "../utils/user__dom.js"
import { detectJwt } from "../utils/user__auth.js"
import { thankyouView } from "./thankyou__page.js"


window.addEventListener("DOMContentLoaded",() => {
    // navigationLeftToHomePage //
    navigationLeftToHomePage();

    // utils //
    const elements = getUserDomElements();
    setupEventListeners(elements);
    detectJwt(elements);

    // thankyou__page //
    thankyouView()
});