import React, { Component } from 'react';


export default class Logo extends Component {

    render() {
      return (
        <div className="App-header">
            <div className="column">
                <p className="bullet">
                    Artifact Archival 
                </p>

                <p className="bullet">
                    Web Scraping
                </p>
            </div>
            <div className="column">
                <img 
                    src={require("../images/A-cubed.png")}
                    alt={"A-cubed"}
                    >
                </img>
            </div>
            <div className="column">
                <p className="bullet">
                    Normalization 
                </p>

                <p className="bullet">
                    File Tranfer
                </p>
            </div>
        </div>
      );
    }      
  }