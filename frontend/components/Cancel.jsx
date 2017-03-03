import React, { Component } from 'react';
import Router from 'react-router/lib/Router';

import rootUrl from '../endpoint.js';

export default class Cancel extends Component {

    constructor(props) {
        super(props);

        this.state = {
            progressColor: ""
        }

        this.performCancel = this.performCancel.bind(this);
    }

    performCancel(ev) {

        ev.preventDefault();

        this.setState({progressColor: "grey" })
        fetch(`${ rootUrl }campaign/${ this.props.params.campaign_id }/cancel/${ this.props.params.secret }/`, {
            method: "POST"
        }).then(res => {
            if (res.ok) {
                this.setState({ cancelled: true })
                this.setState({ progressColor: "rgb(10, 171, 103)" })
            }
            console.log(res)
        }).catch(res => {
            console.log(res)
            this.setState({ progressColor: "" })
        });
    }

    render() {
        return (
            <div className="wrapper">
                <form>
                    <h2>Click to confirm you wish to cancel your campaign:</h2>
                    <button
                        ref="submitButton"
                        onClick={ this.performCancel }
                        style={{ backgroundColor: this.state.progressColor }}>
                        { this.state.cancelled ? "Cancelled!" : "Cancel campaign" }
                    </button>
                </form>
            </div>
        );
    }
}
