import React from "react";
import ReactDOM from "react-dom";
import ScatterExample from './Scatter';
const App = () => {
  return (
    <div>
        <ScatterExample />
    </div>
  );
};
export default App;
ReactDOM.render(<App />, document.getElementById("app"));
