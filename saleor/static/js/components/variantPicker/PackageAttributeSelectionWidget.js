import React, { Component, PropTypes } from 'react';
import classNames from 'classnames';

export default class PackageAttributeSelectionWidget extends Component {

  static propTypes = {
    attribute: PropTypes.object.isRequired,
    handleChange: PropTypes.func.isRequired,
    selected: PropTypes.string
  };

  // handleChange = (attrPk, valuePk) => {
  //   this.props.handleChange(attrPk.toString(), valuePk.toString());
  // }

  handleChange = (event) => {
    let selected = event['srcElement']['options']['selectedIndex'];
    let label = event['srcElement']['options'][selected]['label'];
    let url = this.props.attribute['variants'][selected]['url'];
    let var_id = event['srcElement']['options'][selected]['value'];
    let description = this.props.attribute.variants[selected]['description'];
    let images = this.props.attribute.variants[selected]['images'];
    this.props.handleChange(var_id.toString(), label.toString(), url.toString(), description.toString(), images);
  }

  render() {
    const { attribute, selected } = this.props;
    return (
      <div className="variant-picker">
        <div className="form-group">
        <div className="variant-picker__label">{attribute.name}</div>
        <select className="form-control" data-toggle="option" onChange={() => this.handleChange(event)}>
          {attribute.variants.map((value, i) => {
            const active = selected === value.id.toString();
            return (
              <option value={value.id} selected={active}>
                {value.name}
              </option>
            );
          })}
          </select>
        </div>
      </div>
    );
  }
}
