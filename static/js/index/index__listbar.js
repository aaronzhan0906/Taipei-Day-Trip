import { handleSearch } from "./index__search.js";


const searchInput = document.querySelector(".hero__search-input");
const listBarContainer = document.querySelector(".list-bar__container");


export async function listBarApi() {
    const mrtsUrl = `/api/mrts`;
  
    try {
        const response = await fetch(mrtsUrl);
        const data = await response.json();
        const mrtsData = data.data;
    
        for (let i = 0; i < mrtsData.length; i++) {
            createListBarItem(mrtsData[i]);
        }
        
        leftArrow();
        rightArrow();
    } catch (error) {
        console.log("Error fetching mrts data.", error);
    }
};


function createListBarItem(item) {
    const listBarContainer = document.querySelector(".list-bar__container");
    const listBarItem = document.createElement("div");
    listBarItem.classList.add("list-bar__item");
    listBarItem.addEventListener('click', (event) => handleListBarItemClick(event));
    listBarItem.textContent = item;
    listBarContainer.appendChild(listBarItem);

    
    return listBarContainer;
};


function handleListBarItemClick(event) {
    searchInput.value = event.target.textContent; 
    if (searchInput.value !== null){
        handleSearch();
    }
};


function leftArrow() {
    document.querySelector(".list-bar__arrow--left").addEventListener('click', function(event) {
      const scrollAmount = 0.75 * listBarContainer.clientWidth;
      listBarContainer.scrollLeft -= scrollAmount;
    });
  }
  
  function rightArrow() {
    document.querySelector(".list-bar__arrow--right").addEventListener('click', function(event) {
      const scrollAmount = 0.75 * listBarContainer.clientWidth;
      listBarContainer.scrollLeft += scrollAmount;
    });
  }

