import { userFormSignIn , userFormSignUp, initialSignUp, initialSignIn } from "./user__auth.js"
let isSignIn = true;

export const getUserDomElements = () => {
    return {
        navigationRightSignIn: document.querySelector(".navigation__right-signin"),
        navigationRightBooking: document.querySelector(".navigation__right-booking"),
        user: document.querySelector(".user"),
        userForm: document.querySelector(".user__form"),
        userBox: document.querySelector(".user__box"),
        overlay: document.querySelector(".overlay"),
        formTitle: document.querySelector(".form__title"),
        formFooterQuestion: document.querySelector(".form__footer--question"),
        formFooterRegister: document.querySelector(".form__footer--register"),
        formName: document.querySelector(".form__name"),
        formEmail: document.querySelector(".form__email"),
        formPassword: document.querySelector(".form__password"),
        formSubmit: document.querySelector(".form__submit"),
        formResult: document.querySelector(".form__result"),
        
    };
};

export const setupEventListeners = (elements) => {
    const { navigationRightSignIn, user, overlay, formFooterRegister, formSubmit, formResult } = elements;

    // test //

    navigationRightSignIn.addEventListener("click", () => {
        user.style.display = "block";
        overlay.style.display = "block";
    });

    overlay.addEventListener("click", () => {
        user.style.display = "none";
        overlay.style.display = "none";
    });

    formFooterRegister.addEventListener("click", () => {
        if (isSignIn) {
            initialSignUp(elements);
            isSignIn = false;
        } else {
            initialSignIn(elements);
            isSignIn = true;
        }

        if (formResult.textContent) {
            formResult.textContent = "";
            formResult.style.display = "none";
        }
    });

    formSubmit.addEventListener("click", (event) => {
        event.preventDefault();
        if (isSignIn) {
            console.log("in");
            userFormSignIn(elements);
        } else {
            console.log("up");
            userFormSignUp(elements);
        }
    });
};

