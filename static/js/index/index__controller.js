import { fetchAttractionsData } from "./index__attractions.js";
import { listBarApi } from "./index__listbar.js";
import { searchInputApi } from "./index__search.js";

// utils //
import { getUserDomElements, setupEventListeners } from "../utils/user__dom.js"
import { detectJwt } from "../utils/user__auth.js"
import { navigationLeftToHomePage } from "../utils/navigationLeftToHomePage.js"


window.addEventListener("DOMContentLoaded", () => {
    // attractions //
    fetchAttractionsData();
    listBarApi();
    searchInputApi();

    // user //
    const elements = getUserDomElements();
    setupEventListeners(elements);

    detectJwt(elements)

    // navigationLeftToHomePage //
    navigationLeftToHomePage()
});




