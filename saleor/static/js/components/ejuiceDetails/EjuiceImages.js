import React, {Component, PropTypes} from 'react';
import Img from 'react-image';
import { observer } from 'mobx-react';
// import { Button, Modal, ModalHeader, ModalBody, ModalFooter } from 'reactstrap';

@observer
export default class EjuiceImages extends Component {

  static propTypes = {
    store: PropTypes.object.isRequired,
    ejuice_size: PropTypes.string.isRequired
    // toggle:  PropTypes.func
  }

  // constructor(props) {
  //   super(props);
  //   this.state = {
  //     modal: false
  //   };
  //   this.toggle = this.toggle.bind(this);
  // }
  //
  // toggle() {
  //   this.setState({
  //     modal: !this.state.modal
  //   });
  // }

  render() {
    let selection_id = Object.keys(this.props.store[this.props.ejuice_size])[0];
    let selected_ejuice = this.props.store[this.props.ejuice_size][selection_id];
    let images = selected_ejuice.images;
    let images_srcset = images.one_x + ' 1x ,' + images.two_x + ' 2x';
    let data_target = "#" + this.props.ejuice_size;
    return (
      <div className="col-md-4 col-12 product__gallery">
        <div className="card mb-4 shadow-sm">
          <Img className={'d-block img-fluid'} src={images.one_x} srcSet={images_srcset}/>
            <div className="card-body">
              <h2>{ selected_ejuice.name }</h2>
              {/*<p className="card-text">{ selected_ejuice.description }</p>*/}
                <div className="btn-group">
                  <button type="button" className="btn btn-primary" data-toggle="modal" data-target={data_target}>
                    Details
                  </button>
                </div>

              <div className="modal fade" id={ this.props.ejuice_size } tabIndex="-1" role="dialog"
                   aria-labelledby="exampleModalLongTitle" aria-hidden="true">
                <div className="modal-dialog" role="document">
                  <div className="modal-content">
                    <div className="modal-header">
                      <h5 className="modal-title" id="exampleModalLongTitle">{ selected_ejuice.name }</h5>
                      <button type="button" className="close" data-dismiss="modal" aria-label="Close">
                        <span aria-hidden="true">&times;</span>
                      </button>
                    </div>
                    <div className="modal-body">
                      { selected_ejuice.description }
                    </div>
                    <div className="modal-footer">
                      <button type="button" className="btn btn-secondary" data-dismiss="modal">Close</button>
                    </div>
                  </div>
                </div>
              </div>

            </div>






          {/*<Button color="danger" onClick={this.toggle}>Details</Button>*/}
          {/*<Modal isOpen={this.state.modal} toggle={this.toggle}>*/}
            {/*<ModalHeader toggle={this.toggle}>Modal title</ModalHeader>*/}
            {/*<ModalBody>*/}
              {/*Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.*/}
            {/*</ModalBody>*/}
            {/*<ModalFooter>*/}
              {/*<Button color="primary" onClick={this.toggle}>Do Something</Button>{' '}*/}
              {/*<Button color="secondary" onClick={this.toggle}>Cancel</Button>*/}
            {/*</ModalFooter>*/}
          {/*</Modal>*/}
        </div>
      </div>
    )
  }
}
