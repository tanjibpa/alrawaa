import React, {Component, PropTypes} from 'react';
import Img from 'react-image';
import { observer } from 'mobx-react';

@observer
export default class EjuiceImages extends Component {

  static propTypes = {
    selected_ejuice: PropTypes.object,
    store: PropTypes.object.isRequired
  }

  render() {
    let selection_id = Object.keys(this.props.store.ejuice60Details)[0];
    let selected_ejuice = this.props.store.ejuice60Details[selection_id];
    console.log(selected_ejuice);
    let images = selected_ejuice.images;
    let images_srcset = images.one_x + ' 1x ,' + images.two_x + ' 2x';
    return (
      <div className="col-md-6 col-12 product__gallery">
        <Img className={'d-block img-fluid'} src={images.one_x} srcSet={images_srcset}/>
      </div>
    )
  }
}
