import { createAttractionCard } from "./index__attractions.js";
let isObserverInitialized = false;
let storeNextPage;
let storeKeyword = null;


export function getNextPage(nextPage, keyword){
    storeNextPage = nextPage;
    storeKeyword = keyword;
    return  storeNextPage, storeKeyword;
};


export function handleObserver(nextPage) {
    // console.log("&&& handleObserver &&&");
    const footer = document.querySelector("footer");
    if (isObserverInitialized) return; 

    const options = {
        root: null, 
        rootMargin: "0px",
        threshold: 0.1 
    };

    const observer = new IntersectionObserver((entries) => {
        const entry = entries[0];  
        if (entry.isIntersecting) {
            // console.log("--- touch footer ---");
            storeNextPage !== null 
                ? loadNextPage(storeNextPage, storeKeyword) 
                : console.log("===== NO MORE DATA TO LOAD! =====");
        }
    }, options);
    

    observer.observe(footer);
    isObserverInitialized = true;
};


export async function loadNextPage(storeNextPage, storeKeyword) {
    try {
        const apiUrl = `/api/attractions?page=${storeNextPage}${storeKeyword ? `&keyword=${storeKeyword}` : ""}`;
  
        const response = await fetch(apiUrl);
        const data = await response.json();
        const attractionsData = data.data;
        const nextPage = data.nextPage;
        const keyword = storeKeyword;
        
        for (let i = 0; i < attractionsData.length; i++) {
            createAttractionCard(attractionsData[i]);
        }
    
        // console.log(`### attractionsToLoad: ${nextPage} ###`);
        getNextPage(nextPage, keyword);
        } catch (error) {
        console.log("Error fetching attraction data.", error);
        }
};