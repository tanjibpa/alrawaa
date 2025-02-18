import _ from 'lodash';
import $ from 'jquery';
import classNames from 'classnames';
import { observer } from 'mobx-react';
import React, { Component, PropTypes } from 'react';

import AttributeSelectionWidget from './AttributeSelectionWidget';
import PackageAttributeSelectionWidget from './PackageAttributeSelectionWidget';
import QuantityInput from './QuantityInput';
import * as queryString from 'query-string';
import PackageOfferDevice from './PackageOfferDevice';
import EjuiceDetails from '../ejuiceDetails/EjuiceDetails';
import packageStore from './../../stores/variantPickerPackageOffer';

@observer
export default class VariantPickerPackageOffer extends Component {

  static propTypes = {
    onAddToCartError: PropTypes.func.isRequired,
    onAddToCartSuccess: PropTypes.func.isRequired,
    store: PropTypes.object.isRequired,
    url: PropTypes.string.isRequired,
    // coil_url: PropTypes.string.isRequired,
    // battery_url: PropTypes.string.isRequired,
    // ejuice_60_url: PropTypes.string.isRequired,
    // ejuice_100_url: PropTypes.string.isRequired,
    variantAttributes: PropTypes.array.isRequired,
    variants: PropTypes.array.isRequired
  }

  constructor(props) {
    super(props);
    const { variants, variantsEjuice60, variantsEjuice100 } = this.props;
    const variant = variants.filter(v => !!Object.keys(v.attributes).length);
    const variantEjuice60 = variantsEjuice60.variants.filter(v => !!Object.keys(v.name).length);
    const variantEjuice100 = variantsEjuice100.variants.filter(v => !!Object.keys(v.name).length);
    // console.log(variantEjuice60);
    // console.log(variantEjuice100);

    const params = queryString.parse(location.search);
    let selection = {};
    if (Object.keys(params).length) {
      Object.keys(params).some((name) => {
        const valueName = params[name];
        const attribute = this.matchAttributeBySlug(name);
        const value = this.matchAttributeValueByName(attribute, valueName);
        if (attribute && value) {
          selection[attribute.pk] = value.pk.toString();
        } else {
          // if attribute doesn't exist - show variant
          selection = variant ? variant.attributes : {};
          // break
          return true;
        }
      });
    } else if (Object.keys(variant).length) {
      selection = variant[0].attributes;
    }
    const variantsEjuiuce60Selection = {};
    const variantsEjuiuce100Selection = {};

    variantsEjuiuce60Selection[parseInt(variantsEjuice60.variants[0].id)] = {
      'name': variantsEjuice60.variants[0].name,
      'url':variantsEjuice60.variants[0].url,
      'description': variantsEjuice60.variants[0].description,
      'images': variantsEjuice60.variants[0].images};

    variantsEjuiuce100Selection[parseInt(variantsEjuice100.variants[0].id)] = {
      'name': variantsEjuice100.variants[0].name,
      'url': variantsEjuice100.variants[0].url,
      'description': variantsEjuice100.variants[0].description,
      'images': variantsEjuice100.variants[0].images};

    //set ejuice details to the store
    this.props.store.setEjuice60Details(variantsEjuiuce60Selection);
    this.props.store.setEjuice100Details(variantsEjuiuce100Selection);

    this.state = {
      errors: {},
      quantity: 1,
      selection: selection,
      ejuice60selection: variantsEjuiuce60Selection,
      ejuice100selection: variantsEjuiuce100Selection
    };
    this.matchVariantFromSelection();
  }

  handleAddToCart = () => {
    const {onAddToCartSuccess, onAddToCartError, store} = this.props;
    const {quantity} = this.state;
    let ejuice60VariantId = Object.keys(this.state.ejuice60selection)[0];
    let ejuice100VariantId = Object.keys(this.state.ejuice100selection)[0];
    if (quantity > 0 && !store.isEmpty) {
      $.ajax({
        url: this.props.url,
        method: 'post',
        data: {
          quantity: quantity,
          variant: store.variant.id,
          type: 'package',
          // ejuiceSixty: Object.keys(this.state.ejuice60selection)[0],
          // ejuiceHundred: Object.keys(this.state.ejuice100selection)[0],
          package_offer_id: this.props.packageOfferID,
          coil_variant: this.props.coil_variant,
          battery_variant: this.props.battery_variant,
          ejuice60_variant: ejuice60VariantId,
          ejuice100_variant: ejuice100VariantId,
        },
        success: () => {
          onAddToCartSuccess();
        },
        error: (response) => {
          onAddToCartError(response);
        }
      });
    }
  }

      // $.ajax({
      //   url: this.props.coil,
      //   method: 'post',
      //   data: {
      //     quantity: quantity,
      //     variant: this.props.coil_variant,
      //     type: 'package',
      //     // ejuiceSixty: Object.keys(this.state.ejuice60selection)[0],
      //     // ejuiceHundred: Object.keys(this.state.ejuice100selection)[0],
      //     package_offer_id: this.props.packageOfferID,
      //   },
      //   success: () => {
      //     onAddToCartSuccess();
      //   },
      //   error: (response) => {
      //     onAddToCartError(response);
      //   }
      // });

      // $.ajax({
      //   url: this.props.battery,
      //   method: 'post',
      //   data: {
      //     quantity: quantity,
      //     variant: this.props.battery_variant,
      //     type: 'package',
      //     // ejuiceSixty: Object.keys(this.state.ejuice60selection)[0],
      //     // ejuiceHundred: Object.keys(this.state.ejuice100selection)[0],
      //     package_offer_id: this.props.packageOfferID,
      //   },
      //   success: () => {
      //     onAddToCartSuccess();
      //   },
      //   error: (response) => {
      //     onAddToCartError(response);
      //   }
      // });

      // let ejuice60VariantId = Object.keys(this.state.ejuice60selection)[0];
      // let ejuice60Url = this.state.ejuice60selection[ejuice60VariantId]['url']+'add/';
      // $.ajax({
      //   url: ejuice60Url,
      //   method: 'post',
      //   data: {
      //     quantity: quantity,
      //     variant: ejuice60VariantId,
      //     type: 'package',
      //     // ejuiceSixty: Object.keys(this.state.ejuice60selection)[0],
      //     // ejuiceHundred: Object.keys(this.state.ejuice100selection)[0],
      //     package_offer_id: this.props.packageOfferID,
      //   },
      //   success: () => {
      //     onAddToCartSuccess();
      //   },
      //   error: (response) => {
      //     onAddToCartError(response);
      //   }
      // });

      // let ejuice100VariantId = Object.keys(this.state.ejuice100selection)[0];
      // let ejuice100Url = this.state.ejuice100selection[ejuice100VariantId]['url']+'add/';
      // $.ajax({
      //   url: ejuice100Url,
      //   method: 'post',
      //   data: {
      //     quantity: quantity,
      //     variant: ejuice100VariantId,
      //     type: 'package',
      //     // ejuiceSixty: Object.keys(this.state.ejuice60selection)[0],
      //     // ejuiceHundred: Object.keys(this.state.ejuice100selection)[0],
      //     package_offer_id: this.props.packageOfferID,
      //   },
      //   success: () => {
      //     onAddToCartSuccess();
      //   },
      //   error: (response) => {
      //     onAddToCartError(response);
      //   }
      // });
  //   }
  // }

  handleAttributeChange = (attrId, valueId) => {
    this.setState({
      selection: Object.assign({}, this.state.selection, { [attrId]: valueId })
    }, () => {
      this.matchVariantFromSelection();
      let params = {};
      Object.keys(this.state.selection).forEach(attrId => {
        const attribute = this.matchAttribute(attrId);
        const value = this.matchAttributeValue(attribute, this.state.selection[attrId]);
        if (attribute && value) {
          params[attribute.slug] = value.slug;
        }
      });
      history.pushState(null, null, '?' + queryString.stringify(params));
    });
  }

  handleAttributeChangeEjuice60 = (attrId, valueId, url, description, images) => {
    this.setState(
      {ejuice60selection: {[attrId]: {'name': valueId, 'url': url, 'description': description, 'images': images}}});
      packageStore.setEjuice60Details({
        [attrId]: {'name': valueId, 'url': url, 'description': description, 'images': images}});
  }

  handleAttributeChangeEjuice100 = (attrId, valueId, url, description, images) => {
     this.setState(
      {ejuice100selection: {[attrId]: {'name': valueId, 'url': url, 'description': description, 'images': images}}});
     packageStore.setEjuice100Details({
        [attrId]: {'name': valueId, 'url': url, 'description': description, 'images': images}});
  }

  handleQuantityChange = (event) => {
    this.setState({quantity: parseInt(event.target.value)});
  }

  matchAttribute = (id) => {
    const { variantAttributes } = this.props;
    const match = variantAttributes.filter(attribute => attribute.pk.toString() === id);
    return match.length > 0 ? match[0] : null;
  }

  matchAttributeBySlug = (slug) => {
    const { variantAttributes } = this.props;
    const match = variantAttributes.filter(attribute => attribute.slug === slug);
    return match.length > 0 ? match[0] : null;
  }

  matchAttributeValue = (attribute, id) => {
    const match = attribute.values.filter(attribute => attribute.pk.toString() === id);
    return match.length > 0 ? match[0] : null;
  }

  matchAttributeValueByName = (attribute, name) => {
    const match = attribute ? attribute.values.filter(value => value.slug === name) : [];
    return match.length > 0 ? match[0] : null;
  }

  matchVariantFromSelection() {
    const { store, variants } = this.props;
    let matchedVariant = null;
    variants.forEach(variant => {
      if (_.isEqual(this.state.selection, variant.attributes)) {
        matchedVariant = variant;
      }
    });
    store.setVariant(matchedVariant);
  }

  render() {
    const { store, variantAttributes, variantsEjuice60, variantsEjuice100 } = this.props;
    const { errors, selection, quantity, ejuice60selection, ejuice100selection } = this.state;
    const disableAddToCart = store.isEmpty;
    const addToCartBtnClasses = classNames({
      'btn primary': true,
      'disabled': disableAddToCart
    });

    return (
      <div>
        {variantAttributes.map((attribute, i) =>
          <AttributeSelectionWidget
            attribute={attribute}
            handleChange={this.handleAttributeChange}
            key={i}
            selected={selection[attribute.pk]}
          />
        )}
        <p><u>Choose your ejuices</u></p>
        <PackageAttributeSelectionWidget
          attribute={variantsEjuice60}
          handleChange={this.handleAttributeChangeEjuice60}
          selected={ejuice60selection.id}
        />
        <PackageAttributeSelectionWidget
          attribute={variantsEjuice100}
          handleChange={this.handleAttributeChangeEjuice100}
          selected={ejuice100selection.id}
        />
        <div className="clearfix">
          <div className="form-group product__info__button">
            <button
              className={addToCartBtnClasses}
              onClick={this.handleAddToCart}
              disabled={disableAddToCart}>
              {pgettext('Product details primary action', 'Add to cart')}
            </button>
          </div>
        </div>
        {/*<PackageOfferDevice />*/}
      </div>
    );
  }
}
