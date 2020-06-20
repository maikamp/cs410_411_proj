import React, { Component } from 'react';
import { BrowserRouter as Router, Route } from "react-router-dom"
import './styles/App.css';       
import "bootstrap/dist/css/bootstrap.min.css"

import Navbar from "./components/navbar.component"
import ExercisesList from "./components/exercises-list.component";
import EditExercise from "./components/edit-exercise.component";
import CreateExercise from "./components/create-exercise.component";
import CreateUser from "./components/create-user.component";
import Biography from './components/Biography';

function App() {
  return (
<<<<<<< HEAD
    <Router>
		<Biography/>
=======
    <Router> 
      <Biography/>
      <Navbar> 
        <br/> 
          
          <Route path="/" exact component={ExercisesList} />
          <Route path="/edit/:id" component={EditExercise} />
          <Route path="/create" component={CreateExercise} />
          <Route path="/user" component={CreateUser} />
      
        </Navbar>
    </Router>

  
}

  );
}

export default App;
