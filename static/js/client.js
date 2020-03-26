var stripe = Stripe('pk_test_TYooMQauvdEDq54NiTphI7jx');

// Create an instance of Elements.
var elements = stripe.elements();

// Custom styling can be passed to options when creating an Element.
// (Note that this demo uses a wider set of styles than the guide below.)
var style = {
    base: {
        color: '#32325d',
        fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
        fontSmoothing: 'antialiased',
        fontSize: '16px',
        '::placeholder': {
            color: '#aab7c4'
        }
    },
    invalid: {
        color: '#fa755a',
        iconColor: '#fa755a'
    }
};

// Create an instance of the card Element.
var card = elements.create('card', {
    style: style
});

// Add an instance of the card Element into the `card-element` <div>.
card.mount('#card-element');


// Handle real-time validation errors from the card Element.
card.addEventListener('change', function (event) {
    var displayError = document.getElementById('card-errors');
    if (event.error) {
        displayError.textContent = event.error.message;
    } else {
        displayError.textContent = '';
    }
});

var formPaypal = document.getElementById('paypal-form');
formPaypal.addEventListener('submit', function (event) {
    event.preventDefault()

    var hiddenInputPaypal = document.createElement('input');
    hiddenInputPaypal.setAttribute("type", "hidden");
    hiddenInputPaypal.setAttribute("name", "payment");
    hiddenInputPaypal.setAttribute("value", "paypal");
    formPaypal.appendChild(hiddenInputPaypal);

    // Submit the form
    formPaypal.submit();
})


// Handle form submission.
var formStripe = document.getElementById('stripe-form');
var privacy = document.getElementById('privacy_policy')
var errorElement = document.getElementById('card-errors');
formStripe.addEventListener('submit', function (event) {
    event.preventDefault();

    stripe.createToken(card).then(function (result) {
        if (result.error) {
            // Inform the user if there was an error.
            errorElement.textContent = result.error.message;
        } else if (!privacy.checked) {
            errorElement.textContent = "Accept privacy policy to proceed the data"
        } else {
            // Send the token to your server.
            stripeTokenHandler(result.token);
        }
    });
});

// Submit the form with the token ID.
function stripeTokenHandler(token) {
    // Insert the token ID into the form so it gets submitted to the server
    var formStripe = document.getElementById('stripe-form');
    var hiddenInput = document.createElement('input');
    hiddenInput.setAttribute("type", "hidden");
    hiddenInput.setAttribute("name", "stripeToken");
    hiddenInput.setAttribute("value", token.id);
    formStripe.appendChild(hiddenInput);

    var hiddenInput = document.createElement('input');
    hiddenInput.setAttribute("type", "hidden");
    hiddenInput.setAttribute("name", "payment");
    hiddenInput.setAttribute("value", "stripe");
    formStripe.appendChild(hiddenInput);

    // Submit the form
    formStripe.submit();
}

var currentCardForm = $('.current-card-form');
var newCardForm = $('.new-card-form');
var use_default_card = document.querySelector("input[name=use_default_card]");
use_default_card.addEventListener('change', function () {
    if (this.checked) {
        newCardForm.hide();
        currentCardForm.show()
    } else {
        newCardForm.show();
        currentCardForm.hide()
    }
})