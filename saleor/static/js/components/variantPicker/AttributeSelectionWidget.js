import React, { Component, PropTypes } from 'react';
import classNames from 'classnames';

export default class AttributeSelectionWidget extends Component {

  static propTypes = {
    attribute: PropTypes.object.isRequired,
    handleChange: PropTypes.func.isRequired,
    selected: PropTypes.string
  };

  // handleChange = (attrPk, valuePk) => {
  //   this.props.handleChange(attrPk.toString(), valuePk.toString());
  // }

  handleChange = (event, attrPk) => {
    this.props.handleChange(attrPk.toString(), event.target.value.toString());
  }

  render() {
    const { attribute, selected } = this.props;
    // console.log(attribute);
    return (
      <div className="variant-picker">
        <div className="form-group">
        <div className="variant-picker__label">{attribute.name}</div>
        <select className="form-control" data-toggle="option" onChange={() => this.handleChange(event, attribute.pk)}>
          {attribute.values.map((value, i) => {
            const active = selected === value.pk.toString();
            return (
              <option value={value.pk} selected={active}>
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
