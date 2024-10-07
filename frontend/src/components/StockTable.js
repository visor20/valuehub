import React from 'react';
import './StockTable.css';

const clamp = (value, min, max) =>
{
  return Math.max(min, Math.min(value, max));
}

const setRowStyle = (data) =>
{
  // -zero = most green, +10 = most red
  const clamped_data = clamp(data, 0, 5);
  const r = (clamped_data / 5) * 255;
  const g = 255 - r;
  const b = 80;

  return `rgb(${r}, ${g}, ${b})`
};

const setHeaderStyle = (header, color_key) =>
{
  if (header === color_key)
  {
    return '#FF00FF';
  }
  else
  {
    return '#FFFFFF';
  }
};

const StockTable = (props) => 
{
    if (props.loading)
    {
      return (<p>Waiting...</p>);
    }
    
    if (Object.keys(props.stocks).length === 0 
        || props.stocks === null)
    {
      return (
        <div>
          <p>No data available... Check API limit: </p>
          <a href="https://site.financialmodelingprep.com/developer/docs/dashboard">Here.</a>
        </div>
      );
    }

    const headers = Object.keys(props.stocks[0]);
    const color_key = props.radio_value;

    if (headers.length === 0)
    {
      return (<p>Data is empty</p>);
    }

    return (
    <table className="stock-table">
        <thead>
          <tr>
            {headers.map((header, index) => (
            <th style={{backgroundColor: setHeaderStyle(header, color_key)}} key={index}>{header}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {Object.values(props.stocks).map((item, rowIndex) => (
            <tr style={{backgroundColor: setRowStyle(item[color_key])}} key={rowIndex}>
              {headers.map((header, colIndex) => (
              <td key={colIndex}>{item[header]}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    );
};

export default StockTable;
