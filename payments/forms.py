from django import forms
from .models import PaymentMethod, Payment

class PaymentMethodForm(forms.ModelForm):
    class Meta:
        model = PaymentMethod
        fields = ['payment_type']

class CashInForm(forms.Form):
    amount = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)

class MakePaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['payment_method']

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['payment_method'].queryset = PaymentMethod.objects.filter(user=user)