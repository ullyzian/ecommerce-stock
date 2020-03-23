from django import forms


class CheckoutForm(forms.Form):
    full_name = forms.CharField(max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control', 'name': 'username'})
    )

    card_number = forms.IntegerField(widget=forms.NumberInput(
        attrs={'class': 'form-control', 'name': 'cardNumber'}))

    expiration = forms.ChoiceField(widget=forms.SelectDateWidget(
        attrs={'class': 'form-control', 'style': 'width: 47%;'})
    )

    cvv = forms.IntegerField(min_value=100, max_value=999,
                             widget=forms.NumberInput(attrs={
                                 'class': 'form-control'
                             }))
