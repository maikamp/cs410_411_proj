import React, { Component } from 'react';

import { BrowserRouter as Router, Route } from "react-router-dom"
import "bootstrap/dist/css/bootstrap.min.css"
import ExercisesList from "./exercises-list.component";
import EditExercise from "./edit-exercise.component";
import CreateExercise from "./create-exercise.component";
import CreateUser from "./create-user.component";

export default class Navbar extends Component {

  render() {
    return (
      <Router> 
        <Navbar> 
          <br/>
          <Route path="/edit/:id" component={EditExercise} />
          <Route path="/create" component={CreateExercise} />
          <Route path="/user" component={CreateUser} />

        </Navbar>
      </Router>
    );
  }      
}