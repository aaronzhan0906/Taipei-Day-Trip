// fetch API and get json
export const fetchAttractionIdData = async (attractionId) => {
    const apiAttractionIdUrl = `/api/attraction/${attractionId}`;
    const response = await fetch(apiAttractionIdUrl);
    const status = response.status;

    if (status === 200) {
        const data = await response.json();
        return data.data;
    } else {
        redirectToHomePage(); // if no attractionId, redirect to home page
    }
};