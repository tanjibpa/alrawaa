import React, { Component, PropTypes } from 'react';
import classNames from 'classnames';

export default class PackageAttributeSelection extends Component {

  static propTypes = {
    attribute: PropTypes.object.isRequired,
    handleChange: PropTypes.func.isRequired
  };

  handleChange = (event, attrName) => {
    // this.props.handleChange(attrName.toString(), values);
    let selected = event['srcElement']['options']['selectedIndex'];
    let label = event['srcElement']['options'][selected]['label'];
    let url = this.props.attribute['variant'][selected]['url'];
    let var_id = event['srcElement']['options'][selected]['value'];
    let description = this.props.attribute.variant[selected]['description'];
    let images = this.props.attribute.variant[selected]['images'];
    console.log("FROM PROPS");
    console.log(this.props.attribute.variant[selected]);
    this.props.handleChange(attrName, this.props.attribute.variant[selected]);
  };

  render() {
    const { attribute } = this.props;
    return (
      <div className="variant-picker">
        <div className="form-group">
        <div className="variant-picker__label">{attribute.name}</div>
        <select className="form-control" data-toggle="option" onChange={() => this.handleChange(event, attribute.name)}>
          {attribute.variant.map((value) => {
            return (
              <option value={value.id}>
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
