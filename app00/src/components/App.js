import React, { Component } from 'react';
import ReactDOM from "react-dom";
import LineExample from './Line';

class App extends Component {
  render() {
    return (
      <div className="driver">
        <h2>app00x</h2>
        <LineExample />
      </div>
    );
  }
}

export default App;
ReactDOM.render(<App />, document.getElementById("app"));
