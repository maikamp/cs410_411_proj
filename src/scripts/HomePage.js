import React from 'react';
import logo from './logo.svg';
import './styles/HomePage.css';

function HomePage() {
  return (
    <div className="homePage">

      <div class="sidenav">
        <div class="container-small">
          <a href="https://www.cs.odu.edu/~411crystal/">Home</a>
        </div>
        
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
          href="https://www.cs.odu.edu/~411crystal/"
          target="_blank"
          rel="noopener noreferrer"
        >
          Project Webpage
        </a>
      </header>
    </div>
  );
}

export default homePage;
