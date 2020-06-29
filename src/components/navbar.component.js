import React, { useState, Component } from 'react';
import {  
  NavbarToggler,
  NavbarBrand,
  Nav,
  Navbar, 
  Form, 
  FormControl, 
  Button, 
  Collapse, 
  NavItem,
  NavLink,
  UncontrolledDropdown,
  DropdownToggle,
  NavDropdown, 
  DropdownMenu,
  DropdownItem,
  NavbarText
} from 'react-bootstrap';

import "bootstrap/dist/css/bootstrap.min.css"
import "../styles/nav.css"

export default class Navi extends Component {

  render() {
    return (
      <Navbar className="color-nav" variant="dark">
        <Navbar.Brand>A3</Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="mr-auto"> 
            <Nav.Link href="#../../public/index.html">Home</Nav.Link>
            <Nav.Link href="https://www.cs.odu.edu/~411crystal/home.html">Webpage</Nav.Link>
            <Nav.Link href="#link">About</Nav.Link>
            <NavDropdown title="Account" id="basic-nav-dropdown">
              <NavDropdown.Item href="#action/3.1">Sign Up</NavDropdown.Item>
              <NavDropdown.Item href="#action/3.2">Log In</NavDropdown.Item>
              <NavDropdown.Item href="#action/3.3">Settings</NavDropdown.Item>
              <NavDropdown.Divider />
              <NavDropdown.Item href="#action/3.4">Remove Account</NavDropdown.Item>
            </NavDropdown>
          </Nav>  
          <Form inline>
            <FormControl type="text" placeholder="Search" className="mr-sm-2" />
            <Button variant="outline-success">Search</Button>
          </Form>
       </Navbar.Collapse>
      </Navbar>
    );
  }      
}