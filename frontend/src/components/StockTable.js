import React from 'react';
import './StockTable.css';

const clamp = (value, min, max) =>
{
  return Math.max(min, Math.min(value, max));
}

const setRowStyle = (data) =>
{
  // -zero = most green, +10 = most red
  const clamped_data = clamp(data, -1, 8);
  if (clamped_data < 0 || clamped_data > 7)
  {
    return 'var(--light-red)';
  }
  else if (clamped_data < 2)
  {
    return 'var(--light-green)';
  }
  else if (clamped_data < 3)
  {
    return 'var(--green)';
  }
  else if (clamped_data < 5)
  {
    return 'var(--gray)';
  }
  else
  {
    return 'var(--red)';
  }
};

const setHeaderStyle = (header, color_key) =>
{
  if (header === color_key)
  {
    return 'var(--gray)';
  }
  else
  {
    return 'var(--white)';
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
