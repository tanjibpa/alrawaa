import { computed, observable } from 'mobx';

class VariantPickerStorePackageOffer {
  @observable variant = {}
  // @observable

  setVariant(variant) {
    this.variant = variant || {};
  }

  @computed get isEmpty() {
    return !this.variant.id;
  }
}

const store = new VariantPickerStorePackageOffer();
export default store;
