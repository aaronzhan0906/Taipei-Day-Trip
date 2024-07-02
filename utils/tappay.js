export const setupTapPay = () => {
    TPDirect.card.setup({
        fields: {
            number: {
                element: '#card-number',
                placeholder: '**** **** **** ****'
            },
            expirationDate: {
                element: document.getElementById('card-expiration-date'),
                placeholder: 'MM / YY'
            },
            ccv: {
                element: '#card-ccv',
                placeholder: 'ccv'
            }
        },
        styles: {
            'input': {
                'color': 'gray'
            },
            'input.ccv': {
                // 'font-size': '16px'
            },
            'input.expiration-date': {
                // 'font-size': '16px'
            },
            'input.card-number': {
                // 'font-size': '16px'
            },
            ':focus': {
                'color': 'black'
            },
            '.valid': {
                'color': 'green'
            },
            '.invalid': {
                'color': 'red'
            },
            '@media screen and (max-width: 400px)': {
                'input': {
                    'color': 'orange'
                }
            }
        },
        isMaskCreditCardNumber: true,
        maskCreditCardNumberRange: {
            beginIndex: 6,
            endIndex: 11
        }
    });


    TPDirect.card.onUpdate(function (update) {
        if (update.canGetPrime) {
            // Enable submit button to get prime
            document.querySelector('.confirm__submit').removeAttribute('disabled');
        } else {
            // Disable submit button to get prime
            document.querySelector('.confirm__submit').setAttribute('disabled', true);
        }

        // Handle card type
        if (update.cardType) {
            console.log(`Card type: ${update.cardType}`);
        }

        // Handle field status
        ['number', 'expiry', 'ccv'].forEach(field => {
            const element = document.querySelector(`#card-${field}`);
            if (update.status[field] === 2) {
                element.classList.add('invalid');
                element.classList.remove('valid');
            } else if (update.status[field] === 0) {
                element.classList.add('valid');
                element.classList.remove('invalid');
            } else {
                element.classList.remove('valid', 'invalid');
            }
        });
    });

    const confirmButton = document.querySelector('.confirm__submit');
    confirmButton.addEventListener('click', onSubmit);
};


function onSubmit(event) {
    event.preventDefault();

    const tappayStatus = TPDirect.card.getTappayFieldsStatus();

    if (tappayStatus.canGetPrime === false) {
        alert('無法取得 Prime，請檢查信用卡資訊是否正確');
        return;
    }

    TPDirect.card.getPrime((result) => {
        if (result.status !== 0) {
            alert('取得 Prime 失敗: ' + result.msg);
            return;
        }

        const prime = result.card.prime;
        console.log(prime)
        
        const paymentData = {
            prime: prime,
            order: {
                price: document.querySelector('.confirm__cost--variable').textContent,
                trip: document.querySelector('.section__attraction--variable').textContent,
                date: document.querySelector('.section__date--variable').textContent,
                time: document.querySelector('.section__time--variable').textContent
            },
            contact: {
                name: document.querySelector('.contact__form--name').value,
                email: document.querySelector('.contact__form--email').value,
                phone: document.querySelector('.contact__form--telephone').value
            }
        };

        sendPaymentToServer(paymentData);
    });
}

function sendPaymentToServer(paymentData) {
    fetch('/api/payment', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(paymentData),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('付款成功！');
        } else {
            alert('付款失敗：' + data.message);
        }
    })
    .catch(error => {
        console.error('支付請求錯誤:', error);
        alert('發生錯誤，請稍後再試');
    });
}