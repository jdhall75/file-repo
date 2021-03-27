import React from "react";
import './modal.css'

const Modal = ({ fileData, handleClose, show, children }) => {
  const showHideClassName = show ? "modal d-block" : "modal d-none";

  return (
    <div className={showHideClassName}>
    <div className="modal-dialog" role="document">
        <div className="modal-content">
            {children}
        </div>
    </div>
    </div>
  );
};

export default Modal;
