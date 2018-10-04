import React from 'react';
import ReactDOM from 'react-dom';

import VariantPicker from './variantPicker/VariantPicker';
import VariantPickerPackageOffer from './variantPicker/VariantPickerPackageOffer';
import VariantPrice from './variantPicker/VariantPrice';
import store from '../stores/variantPickerPackageOffer';

import {onAddToCartSuccess, onAddToCartError} from './cart';

export default $(document).ready((e) => {
  const variantPickerContainer = document.getElementById('variant-picker-package-offer');
  // const variantPriceContainer = document.getElementById('variant-price-component');

  if (variantPickerContainer) {
    const variantPickerData = JSON.parse(variantPickerContainer.dataset.variantPickerData);
    const variantPickerDataEjuice60 = JSON.parse(variantPickerContainer.dataset.ejuiceSixty);
    const variantPickerDataEjuice100 = JSON.parse(variantPickerContainer.dataset.ejuiceHundred);
    ReactDOM.render(
      <VariantPickerPackageOffer
        onAddToCartError={onAddToCartError}
        onAddToCartSuccess={onAddToCartSuccess}
        store={store}
        url={variantPickerContainer.dataset.action}
        variantAttributes={variantPickerData.variantAttributes}
        variants={variantPickerData.variants}
        variantsEjuice60={variantPickerDataEjuice60}
        variantsEjuice100={variantPickerDataEjuice100}
        packageOfferID={variantPickerContainer.dataset.packageOfferId}
        coil={variantPickerContainer.dataset.coil}
        coil_variant={variantPickerContainer.dataset.coilVariant}
        battery={variantPickerContainer.dataset.battery}
        battery_variant={variantPickerContainer.dataset.batteryVariant}
      />,
      variantPickerContainer
    );
  }
});
