import React from 'react';
import './TitleBar.css';
import logo from './TitleBarAssets/logo.png'

const TitleBar = (props) =>
{
  return(
    <div className="title-bar-container">
      <div className="title-bar-logo">
        <img src={logo} alt="logo" />
      </div>
      <div className="title-bar-text1">
        <h1>{props.word1}</h1>
      </div>
      <div className="title-bar-text2">
        <h1>{props.word2}</h1>
      </div>
    </div>
  );
};

export default TitleBar;
