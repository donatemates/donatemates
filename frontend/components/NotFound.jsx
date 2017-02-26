import React, { Component } from 'react';

export default class NotFound extends Component {

    render() {
        return (
            <div className="wrapper">
                <div className="fourohfour-indicator">
                    404
                    <small>{"Ain't nothing here."}
                        &nbsp;<a href="/">{"Create a match campaign?"}</a>
                    </small>
                </div>
            </div>
        );
    }
}
