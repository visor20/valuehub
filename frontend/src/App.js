import './App.css';
import React from 'react';
import { useState } from 'react';
import StockTable from './components/StockTable';
import TitleBar from './components/TitleBar';

function App()
{
  // use state hooks (arg == default) returns the state and a function to update state
  const [lookback, set_lookback] = useState(1);
  const [cluster_val, set_cluster_val] = useState(1);
  const [stocks, set_stocks] = useState({});
  const [loading, set_loading] = useState(true);
  const [radio_value, set_radio_value] = useState("PS");

  const handle_submit = () =>
  {
    // Send the GET request to Flask with slider values as query parameters
    fetch(`http://localhost:5000/api/stocks?lookback=${lookback}&cluster_val=${cluster_val}`, {method: 'GET'})
      .then(response => response.json()) // "promise" body converted to a json...
      .then(data => {
        set_loading(false);
        set_stocks(data); // Set the returned stocks in state
      })
      .catch((error) => {
        set_loading(false);
        console.error('Error fetching stocks:', error);
      });
  };

  const handle_radio_change = (changeEvent) =>
  {
	set_radio_value(changeEvent.target.value);	
  };

  return (
    <div className="app">
      <TitleBar word1={"Value"} word2={"Hub"} />
      <div className="main-container">
        <div className="slider-container">
          <div className="slider">
            <label>Lookback (in days): {lookback}</label>
            <input
              type="range"
              min="1"
              max="28"
              value={lookback}
              onChange={(e) => set_lookback(e.target.value)}
            />
          </div>
          <div className="slider">
            <label>Number of inside buyers: {cluster_val}</label>
            <input
              type="range"
              min="1"
              max="10"
              value={cluster_val}
              onChange={(e) => set_cluster_val(e.target.value)}
            />
          </div>
		<form>
                        <label className="radio">
                              <input type="radio" value="PS" checked={radio_value === "PS"} onChange={handle_radio_change}/>
                              <span class="radio-design"></span>
                              P/S
                        </label>
                        <label className="radio">
                              <input type="radio" value="PB" checked={radio_value === "PB"} onChange={handle_radio_change}/>
                              <span class="radio-design"></span>
                              P/B
                        </label>
                        <label className="radio">
                              <input type="radio" value="PE" checked={radio_value === "PE"} onChange={handle_radio_change}/>
                              <span class="radio-design"></span>
                              P/E
                        </label>
		  </form>
          <button onClick={handle_submit}>Submit</button>
        </div>

        <div className="table-container">
          <StockTable loading={loading} stocks={stocks} radio_value={radio_value}/>
        </div>
      </div>
    </div>
  );
}

export default App;
