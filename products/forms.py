from django import forms


class CheckoutForm(forms.Form):
    """Collect shipping/contact details before placing an order."""

    first_name = forms.CharField(max_length=150, label="First Name")
    last_name = forms.CharField(max_length=150, label="Last Name")
    phone_number = forms.CharField(max_length=20, label="Phone Number")
    house_number = forms.CharField(max_length=50, label="House Number")
    road_number = forms.CharField(max_length=50, label="Road Number")
    postal_code = forms.CharField(max_length=20, label="Postal Code")
    district = forms.CharField(max_length=100, label="District")
    note = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
        label="Order Note (Optional)",
    )
