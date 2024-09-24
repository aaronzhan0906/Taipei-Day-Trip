export const renderAttractionPage = (attractionIdData) => {
    const sectionImage = document.querySelector(".section__image");
    const imageArrowLeft = document.querySelector(".image__arrow--left");
    const imageArrowRight = document.querySelector(".image__arrow--right");
    const imageCircle = document.querySelector(".image__circle")
    const images = attractionIdData.images.slice(0, 13);
    const sectionInfo = document.querySelector(".section__info");
    
    let currentImageIndex = 0;

    const preloadFirstImage = () => {
        const firstImage = new Image();
        firstImage.src = images[0];
        
        firstImage.onload = () => {
            const link = document.createElement("link");
            link.rel = "preload";
            link.as = "image";
            link.fetchPriority = "high";
            link.href = images[0];
            document.head.appendChild(link);

            preloadRemainingImages(images);
        };
    };
    preloadFirstImage();

    const initialImage = (initialIndex) => {
        sectionImage.style.backgroundImage = `url(${images[initialIndex]})`;
        sectionImage.style.opacity = 1;
    };

    for (let i = 0; i < images.length; i++) {
        const imageWhiteCircle = document.createElement("div");
        imageWhiteCircle.classList.add("image__circle--white");
        imageCircle.appendChild(imageWhiteCircle);
    };

    const whiteCircles = document.querySelectorAll(".image__circle--white");
    const changeToBlack = (nextIndex) => {
        whiteCircles.forEach(circle => circle.classList.replace("image__circle--black", "image__circle--white"));
        whiteCircles[nextIndex].classList.replace("image__circle--white", "image__circle--black");
    }

    initialImage(currentImageIndex);
    changeToBlack(currentImageIndex);

    imageArrowLeft.addEventListener("click", () => {
        currentImageIndex = (currentImageIndex - 1 + images.length) % images.length;
        updateImage(currentImageIndex);
        changeToBlack(currentImageIndex);
    });

    imageArrowRight.addEventListener("click", () => {
        currentImageIndex = (currentImageIndex + 1) % images.length;
        updateImage(currentImageIndex);
        changeToBlack(currentImageIndex);
    });

    const updateImage = (Index) => {
        sectionImage.style.opacity = 0;
    
        setTimeout(() => {
            sectionImage.style.backgroundImage = `url(${images[Index]})`;
            sectionImage.style.opacity = 1;
        }, 300); 
    };

    // textContent
    const setTextContent = (selector, text) => {
        const element = document.querySelector(selector);
        if (element) {
            element.textContent = text;
        }
    };

    setTextContent(".section__name", attractionIdData.name);
    setTextContent(".section__subtitle--category", attractionIdData.category);
    setTextContent(".section__subtitle--mid", "at")
    setTextContent(".section__subtitle--mrt", attractionIdData.mrt);
    setTextContent(".main__description", attractionIdData.description);
    setTextContent(".main__address--title", "景點地址：");
    setTextContent(".main__address--content", attractionIdData.address);
    setTextContent(".main__transport--title", "交通方式：");
    setTextContent(".main__transport--content", attractionIdData.transport);
    sectionInfo.style.display = "block";
};

// preload
const preloadRemainingImages = (images) => {
    images.slice(1).forEach(src => {
        document.head.appendChild(Object.assign(document.createElement("link"), {
            rel: "preload",
            as: "image",
            href: src
        }));
    });
};