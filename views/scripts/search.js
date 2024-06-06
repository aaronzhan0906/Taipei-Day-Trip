import { createAttractionCard } from "./attractions.js";
import { handleObserver, getNextPage } from "./pagination.js";

export async function searchInputApi() {
    const searchInput = document.querySelector(".hero__search-input");
    const searchButton = document.querySelector(".hero__search-button");

    const handleSearch = async () => {
        const keyword = searchInput.value;
        const searchApiUrl = `/api/attractions?page=0&keyword=${keyword}`;

        try {
        const response = await fetch(searchApiUrl);
        const data = await response.json();
        const attractionsData = data.data;
        const nextPage = data.nextPage;
        const attractionsContainer = document.querySelector(".attractions");
        attractionsContainer.textContent = "";

        for (let i = 0; i < attractionsData.length; i++) {
            createAttractionCard(attractionsData[i]);
        }

        console.log(`%%% searchToLoad:${nextPage}, ${keyword} %%%`);
        handleObserver();
        getNextPage(nextPage, keyword);
        } 

        catch (error) {
        console.log("Error fetching attraction data.", error);
        }
    };

    searchButton.addEventListener("click", handleSearch);
    searchInput.addEventListener("keydown", (event) => {
        if (event.key === "Enter") {
        handleSearch();
        }
    });
}