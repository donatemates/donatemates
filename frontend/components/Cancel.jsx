import React, { Component } from 'react';
import { Router, Link } from 'react-router';

import rootUrl from '../endpoint.js';

export default class Cancel extends Component {

    constructor(props) {
        super(props);

        this.state = {
            progressColor: ""
        }

        this.performCancel = this.performCancel.bind(this);
    }

    performCancel() {
        this.setState({progressColor: "grey" })
        fetch(`${ rootUrl }campaign/${ this.props.params.campaign_id }/cancel/${ this.props.params.secret }`, {
            method: "PUT"
        }).then(res => {
            if (res.ok) {
                this.setState({ cancelled: true })
                this.setState({ progressColor: "rgb(10, 171, 103)" })
            }
        }).catch(res => {
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
                        Cancel campaign
                    </button>
                </form>
            </div>
        );
    }
}
