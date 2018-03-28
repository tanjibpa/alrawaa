from django import forms
from ...product.models import (Product,ProductClass)


class PackageOfferForm2(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        coil_class_id = ProductClass.objects.filter(name='Coil')[0].id
        coils = Product.objects.filter(product_class_id=coil_class_id)

        battery_class_id = ProductClass.objects.filter(name='Battery')[0].id
        batteries = Product.objects.filter(product_class_id=battery_class_id)

        self.fields['device'] = forms.CharField(label='Device')
        self.fields['device'].widget.attrs['readonly'] = True
        self.fields['coils'] = forms.ChoiceField(
            choices=[(coil.id, coil.name) for coil in coils]
        )
        self.fields['batteries'] = forms.ChoiceField(
            choices=[(battery.id, battery.name) for battery in batteries]
        )
        self.fields['price'] = forms.DecimalField(label='Price', decimal_places=2)
