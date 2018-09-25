import React, {Component, PropTypes} from 'react';
import Img from 'react-image';
import { observer } from 'mobx-react';

@observer
export default class EjuiceImages extends Component {

  static propTypes = {
    store: PropTypes.object.isRequired,
    ejuice_size: PropTypes.string.isRequired
  }

  render() {
    let selection_id = Object.keys(this.props.store[this.props.ejuice_size])[0];
    let selected_ejuice = this.props.store[this.props.ejuice_size][selection_id];
    let images = selected_ejuice.images;
    let images_srcset = images.one_x + ' 1x ,' + images.two_x + ' 2x';
    return (
      <div className="col-md-4 col-12 product__gallery">
        <Img className={'d-block img-fluid'} src={images.one_x} srcSet={images_srcset}/>
      </div>
    )
  }
}
