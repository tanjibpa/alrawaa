import React, { Component, PropTypes } from 'react';
import Img from 'react-image';

export default class PackageAttributeSelection extends Component {

  static propTypes = {
    attribute: PropTypes.object.isRequired,
    handleChange: PropTypes.func.isRequired,
    store: PropTypes.object.isRequired
  };

  handleChange = (event, attrName) => {
    // this.props.handleChange(attrName.toString(), values);
    let selected = event['srcElement']['options']['selectedIndex'];
    // let label = event['srcElement']['options'][selected]['label'];
    // let url = this.props.attribute['variant'][selected]['url'];
    // let var_id = event['srcElement']['options'][selected]['value'];
    // let description = this.props.attribute.variant[selected]['description'];
    // let images = this.props.attribute.variant[selected]['images'];
    this.props.handleChange(attrName, this.props.attribute.variant[selected]);
  };

  render() {
    const { attribute, store } = this.props;
    console.log(store.PackageDetails['Battery'][0]);
    let trimmedId = attribute.name.toString().split(' ').join('');
    return (
      <div className="variant-picker">
        <div className="form-group">
          <div className="variant-picker__label">
            Select {attribute.name}
            <span><button type="button" className="btn btn-light" data-toggle="modal" data-target={"#"+trimmedId}>
              Show details
            </button></span>
          </div>
          <select className="form-control" data-toggle="option" onChange={() => this.handleChange(event, attribute.name)}>
          {attribute.variant.map((value) => {
            return (
              <option value={value.id}>
                {value.product_name} ({value.name})
              </option>
            );
          })}
          </select>
        </div>

        <div className="modal fade" id={trimmedId} tabIndex="-1" role="dialog"
             aria-labelledby="exampleModalLongTitle" aria-hidden="true">
          <div className="modal-dialog" role="document">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title" id="exampleModalLongTitle">{store.PackageDetails[attribute.name][0]['product_name']}</h5>
                <button type="button" className="close" data-dismiss="modal" aria-label="Close">
                  <span aria-hidden="true">&times;</span>
                </button>
              </div>
              <div className="modal-body">
                <Img className={'d-block img-fluid'} src={store.PackageDetails[attribute.name][0].images.one_x} />
                <br/>
                <small>{store.PackageDetails[attribute.name][0]['name']}</small>
                <br/>
                {store.PackageDetails[attribute.name][0]['description']}
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" data-dismiss="modal">Close</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }
}
