import React from "react";
import ReactDOM from "react-dom";
import LineExample from './Line';
const App = () => {
  return (
    <div>
        <LineExample />
    </div>
  );
};
export default App;
ReactDOM.render(<App />, document.getElementById("app"));
