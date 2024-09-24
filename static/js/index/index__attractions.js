import { handleObserver, getNextPage } from "./index__pagination.js"
import { navigationLeftToHomePage } from "../utils/navigationLeftToHomePage.js"



export async function fetchAttractionsData() {
    const apiUrl = `/api/attractions`;
  
    try {
        const response = await fetch(apiUrl);
        const data = await response.json();
        const attractionsData = data.data;
        const nextPage = data.nextPage;
  
        for (let i = 0; i < attractionsData.length; i++) {
            createAttractionCard(attractionsData[i]);
        }
  
        // console.log(`### attractionsToLoad:${nextPage} ###`);
        handleObserver();
        getNextPage(nextPage);
        navigationLeftToHomePage();
    } 
    catch (error) {
        console.log("(attractions) Error fetching attraction data.", error);
    }
};


export function createAttractionCard(data) {
    // attractions container
    const attractions = document.querySelector(".attractions");

    // cards
    const attractionCard = document.createElement("div");
    attractionCard.classList.add("attraction-card");

    // images
    const attractionCardImage = document.createElement("div");
    attractionCardImage.classList.add("attraction-card__image");
    attractionCardImage.style.backgroundImage = `url(${data.images[0]})`;

    const attractionCardName = document.createElement("div");
    attractionCardName.classList.add("attraction-card__name");
    attractionCardName.textContent = data.name;
    attractionCardImage.appendChild(attractionCardName);

    // Details
    const attractionCardDetails = document.createElement("div");
    attractionCardDetails.classList.add("attraction-card__details");

    const attractionCardMrt = document.createElement("div");
    attractionCardMrt.classList.add("attraction-card__mrt");
    attractionCardMrt.textContent = data.mrt;

    const attractionCardCategory = document.createElement("div");
    attractionCardCategory.classList.add("attraction-card__category");
    attractionCardCategory.textContent = data.category;

    // Link
    const link = document.createElement("a");
    const currentUrl = window.location.href;
    const newUrl = `${currentUrl}attraction/${data.id}`
    link.style.textDecoration = "none";
    link.href = newUrl;

    // append
    attractionCardDetails.appendChild(attractionCardMrt);
    attractionCardDetails.appendChild(attractionCardCategory);
    attractionCard.appendChild(attractionCardImage);
    attractionCard.appendChild(attractionCardDetails);
    attractions.appendChild(attractionCard);
    link.appendChild(attractionCard); 
    attractions.appendChild(link);

    return attractionCard;
};