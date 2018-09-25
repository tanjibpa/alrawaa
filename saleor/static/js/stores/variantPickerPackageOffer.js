import { computed, observable } from 'mobx';

class VariantPickerStorePackageOffer {
  @observable variant = {}
  @observable ejuice60Details = {};

  setVariant(variant) {
    this.variant = variant || {};
  }

  setEjuice60Details(details) {
    this.ejuice60Details = details;
  }

  @computed get Ejuice60Details() {
    return this.ejuice60Details;
  }

  @computed get isEmpty() {
    return !this.variant.id;
  }
}

const packageStore = new VariantPickerStorePackageOffer();
export default packageStore;
