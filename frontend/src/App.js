import React, {useEffect, useState} from 'react';


function App() {

  const [data, setData ] = useState(null);
  const path = "";

  useEffect(() => {
      const fetchData = async () => {
          const resp = await fetch(`https://file-repo.jdhall75.repl.co/web${path}`);
          const newData = resp.json();
          setData(newData);
      }
      fetchData();

  }, [path])

  console.log(data)
  return (
      <div>Hello</div>
  );
}

export default App;
