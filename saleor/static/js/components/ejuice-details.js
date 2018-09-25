import React from 'react';
import ReactDOM from 'react-dom';
import packageStore from '../stores/variantPickerPackageOffer';
import EjuiceDetails from './ejuiceDetails/EjuiceDetails';

export default $(document).ready((e) => {
  const ejuiceContainer = document.getElementById('ejuice-details');
  if (ejuiceContainer) {
    ReactDOM.render(
      <EjuiceDetails
        store={packageStore}
      />,
      ejuiceContainer
    );
  }

});
