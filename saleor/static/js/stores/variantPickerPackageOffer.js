import { computed, observable } from 'mobx';

class VariantPickerStorePackageOffer {
  @observable variant = {};
  @observable packageDetails = {};
  @observable ejuice60Details = {};
  @observable ejuice100Details = {};

  setVariant(variant) {
    this.variant = variant || {};
  }

  setPackageDetails(attrName, details) {
    this.packageDetails[attrName] = details;
  }

  setEjuice60Details(details) {
    this.ejuice60Details = details;
  }

  setEjuice100Details(details) {
    this.ejuice100Details = details;
  }

  @computed get PackageDetails() {
    return this.packageDetails;
  }

  @computed get Ejuice60Details() {
    return this.ejuice60Details;
  }

  @computed get Ejuice100Details() {
    return this.ejuice100Details;
  }

  @computed get isEmpty() {
    return !this.variant.id;
  }
}

const packageStore = new VariantPickerStorePackageOffer();
export default packageStore;
