import React, {Component, PropTypes} from 'react';
import ReactDOM from 'react-dom';
import { observer } from 'mobx-react';
import EjuiceImages from './EjuiceImages';
import store from './../../stores/variantPickerPackageOffer';

// @observer
export default class EjuiceDetails extends Component {

  static propTypes = {
    store: PropTypes.object.isRequired
  };

  render () {
    // let selected_id = Object.keys(this.props.selected)[0];
    // let selected_ejuice = this.props.selected[selected_id];
    return (
      <div className={"row"}>
        {/*<div className={"col-md-2"}></div>*/}
        <EjuiceImages
          store={this.props.store}
          ejuice_size={'ejuice60Details'}/>
        <EjuiceImages
          store={this.props.store}
          ejuice_size={'ejuice100Details'}/>
      </div>
    );
  }
}

// export default function EjuiceDetails(props) {
//   const ejuice60Container = document.getElementById(props.containerName);
//   if (!ejuice60Container) {
//     ReactDOM.render(
//       <EjuiceImages/>,
//       ejuice60Container
//     );
//   }
// }

// return (
//       ReactDOM.render(
//         <EjuiceImages selected={selected_ejuice} />,
//         ejuice60Container
//       )
//     );
