import React from 'react';
import logo from './logo.svg';
import './App.css';

function App() {
  return (
    <div className="App">

      <div class="topnav">
        <a href="https://www.cs.odu.edu/~410crystal/">Home</a>
        <a href="#news">Log In</a>
        <a href="#contact">Sign Up</a>
        <a href="#about">About</a> 
        <b href =""> Search </b>
        <input type="text" placeholder="..."></input>
      </div>

      <header className="App-header">
        <img src="./images/A-cubed.png" alt="logo" />
        <p>
          Welcome to A<sup>3</sup>
        </p>
        <a
          className="App-link"
          href="https://www.cs.odu.edu/~410crystal/"
          target="_blank"
          rel="noopener noreferrer"
        >
          Project Webpage
        </a>
      </header>
    </div>
  );
}

export default App;
