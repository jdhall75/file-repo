import React, {useEffect, useState} from 'react';
import Modal from './components/Modal';


function App() {

  const defaultState = {
      "path": "",
      "directories": [],
      "files": [{"name": "", "stat_result": ["","",""]}],
      "url": "",
      "path_parent": ""
  }
  const [ filedata, setfiledata ] = useState(defaultState);
  const [ path, setPath ] = useState("");
  const [ modal, setModal ] = useState({"modal": false, "fileData": {"name": "", "content": ""}});

  const base_url = "https://file-repo.jdhall75.repl.co/web/"

  const loadData = async (uri) => {
      const response = await fetch(`${base_url}${uri}`)
      const json_data = await response.json();
      setfiledata(json_data)
      console.log(json_data)
  }

  const fileClickHandler = async (e, uri) => {
      e.preventDefault();
      const response = await fetch(`${base_url}${uri}`)
      const json_data = await response.json();
      modalOpen(json_data);
      console.log(filedata);
  }

  const dirClickHandler = (e, dir_path) => {
      e.preventDefault(); 
      console.log(dir_path);
      loadData(dir_path);
  }

  useEffect(() => {
    loadData(path);
    console.log(filedata);
  }, []);

  const modalOpen = (fileData) => {
    const modal_state = {
        "modal": true,
        "fileData": fileData
    }
    setModal(modal_state);
    console.log(modal_state)
  };

  const modalClose = (e) => {
    e.preventDefault();
    const modal_state = {
        "modal": false,
        "fileData": {"name": "", "content": ""} 
    }
      setModal(modal_state);
  };

  const epochToDate = (epoch) => {
      let epochNum = Number(epoch);
      let date = new Date(epochNum * 1000);
      return String(date);
  }

  return (
      <>
        <thead>
           <tr>
            <th scope="column">Name</th>
            <th scope="column">Size</th>
            <th scope="column">Last Changed</th>
           </tr> 
        </thead>
        <tbody>
            {(filedata.path_parent !== filedata.path) ? 
            <tr>
               <td>
                    <a href="#" onClick={e => dirClickHandler(e, `${filedata.path_parent}`)}>../(UP)</a>
                </td>
            </tr> : ''
            }
            {filedata.directories.map(d => (
                <tr>
                    <td><i className="glyphicon glyphicon-folder-close"></i>
                        <a href="#" onClick={e => dirClickHandler(e, `${filedata.path}${d}`)}>{ d }</a>
                    </td>
                    <td></td>
                    <td></td>
                </tr>
            ))}
            {filedata.files.map(f => (
                <tr>
                    <td><i className="glyphicon glyphicon-file"></i>
                        <a href="#" onClick={e => fileClickHandler(e, `${filedata.path}/${f.name}`)}>{ f.name }</a>
                    </td>
                    <td>{ f.stat_result[0] }</td>
                    <td>{ epochToDate(f.stat_result[2]) }</td>
                </tr>
            ))}
        </tbody>
        <Modal show={modal.modal} handleClose={e => modalClose(e)} fileData="">
            <div className="modal-header">
                <h5 className="modal-title">{modal.fileData.name}</h5>
                <button type="button" className="close" data-dismiss="modal" aria-label="Close" onClick={e => modalClose(e)} >
                    <span aria-hidden="true">&times;</span>
                </button>
            </div>
            <div className="modal-body">
                <pre>{modal.fileData.content}</pre>
            </div>
            <div className="modal-footer">
                <button type="button" className="btn btn-secondary" data-dismiss="modal" onClick={e => modalClose(e) }>Close</button>
            </div> 
        </Modal>
      </>
  );
}

export default App;
