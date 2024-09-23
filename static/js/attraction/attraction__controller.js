import { fetchAttractionIdData } from "./attraction__fetchAttractionIdData.js"
import { renderAttractionPage  } from "./attraction__page.js"
import { attractionHandler } from "./attraction__attractionHandler.js"
// utils // 
import { navigationLeftToHomePage } from "../utils/navigationLeftToHomePage.js"
import { getUserDomElements, setupEventListeners } from "../utils/user__dom.js"
import { detectJwt } from "../utils/user__auth.js"


window.addEventListener("DOMContentLoaded",() => {
    const attractionId = getIdFromUrl();
    fetchAttractionIdData(attractionId)
    .then(renderAttractionPage)
    .catch(error => console.error("(attractionId) Error fetching attraction data.", error));
    
    // handler //
    attractionHandler();

    // user // 
    const elements = getUserDomElements();
    setupEventListeners(elements);
    detectJwt(elements);

    // navigationLeftToHomePage //
    navigationLeftToHomePage()
});


// get attractionId
const getIdFromUrl = () => {
    const urlParts = window.location.href.split("/");
    return parseInt(urlParts[urlParts.length - 1], 10);
};



