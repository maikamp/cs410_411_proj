import React from 'react';
import ReactDOM from 'react-dom';
import './styles/index.css';

import Logo from "./components/logo-component"; 
import Navi from "./components/navbar.component"; 
import Footer from './components/footer-component';

ReactDOM.render(<Logo/>, document.getElementById('header'));
ReactDOM.render(<Navi/>, document.getElementById('navbar'));
ReactDOM.render(<Footer/>, document.getElementById('footer'));
