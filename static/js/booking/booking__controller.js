import { navigationLeftToHomePage } from "../utils/navigationLeftToHomePage.js"
import { getUserDomElements, setupEventListeners } from "../utils/user__dom.js"
import { detectJwt } from "../utils/user__auth.js"

// booking //
import { bookingView } from "./booking__page.js"



window.addEventListener("DOMContentLoaded",() => {
    // navigationLeftToHomePage //
    navigationLeftToHomePage();

    // utils //
    const elements = getUserDomElements();
    setupEventListeners(elements);
    detectJwt(elements);

    // booking__page //
    bookingView();
});




