import ReactDOM from "react-dom";
import React from "react";
//import { getData } from "./utils"
import Chart from './Chart';
import {tsvParse} from "d3-dsv";
import {timeParse} from "d3-time-format";

function parseData(parse) {
	return function(d) {
		d.date = parse(d.date);
		d.open = +d.open;
		d.high = +d.high;
		d.low = +d.low;
		d.close = +d.close;
		d.volume = +d.volume;

		return d;
	};
}

const parseDate = timeParse("%Y-%m-%d");

function getData2() {
	const promiseMSFT = fetch("https://cdn.rawgit.com/rrag/react-stockcharts/master/docs/data/MSFT.tsv")
		.then(response => response.text())
		.then(data => tsvParse(data, parseData(parseDate)))
	return promiseMSFT;
}

class App extends React.Component  {
	constructor(props) {
		super(props);
		console.log("constructor");
	}

    componentDidMount() {
		console.log("componentDidMount");
		getData2().then(data => {
			this.setState({ data })
		})
	}
    render() {
        if (this.state == null) {
			console.log("TEST01");
			console.log(this);
			return <div>Loading...</div>
		} 
        return (
            <div className="driver">
                <h2>app03</h2>
                <Chart type="svg" data={this.state.data} />
            </div>
        );
    }
}

export default App;
ReactDOM.render(<App />, document.getElementById("app"));
