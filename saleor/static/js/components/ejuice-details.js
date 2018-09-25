import React from 'react';
import ReactDOM from 'react-dom';
import packageStore from '../stores/variantPickerPackageOffer';
import EjuiceDetails from './ejuiceDetails/EjuiceDetails';

export default $(document).ready((e) => {
  const ejuice60Container = document.getElementById('ejuice-60-details');
  if (ejuice60Container) {
    ReactDOM.render(
      <EjuiceDetails
        store={packageStore}
      />,
      ejuice60Container
    );
  }

});
