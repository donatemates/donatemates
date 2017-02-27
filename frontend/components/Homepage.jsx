import React, { Component } from 'react';
import { Link } from 'react-router';

import rootUrl from '../endpoint.js';

export default class Homepage extends Component {

    constructor(opts) {
        super(opts);

        this.state = {
            options: []
        }

        this.submitForm = this.submitForm.bind(this);
    }

    submitForm(ev) {

        ev.preventDefault();

        if (!this.refs.name.value) { alert("Please provide a valid name."); }
        if (!this.refs.amount.value) { alert("Please provide a valid amount."); }
        if (!this.refs.charity.value) { alert("Please provide a valid charity."); }
        if (!this.refs.email.value) { alert("Please provide a valid email."); }

        let campaign = {
            campaigner_name: this.refs.name.value,
            match_cents: parseFloat(this.refs.amount.value) * 100,
            charity_id: this.refs.charity.value,
            campaigner_email: this.refs.email.value
        };

        fetch(`${ rootUrl }campaign/`, {
            method: "POST",
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(campaign)
        }).then(res => {
            res.json().then(json => {
                console.log(json)
            })
        });
    }

    componentDidMount() {
        fetch(`${ rootUrl }charities/`).then(res => {
            if (res.ok) {
                res.json().then(availableCharities => {
                    this.setState({
                        options: availableCharities
                    })
                })
            }
        });
    }

    render() {
        return (
            <div className="wrapper">
                <h1>donatemates</h1>
                <ol className="how-it-works">
                    <li><span>1</span>Create your match campaign</li>
                    <li><span>2</span>Share it with friends and followers</li>
                    <li><span>3</span>Get updates on every match</li>
                </ol>
                <form>
                    <h2>Create a match campaign:</h2>
                    <div className="container">
                        <div className="half relative">
                            <label htmlFor="amount">I will match up to:</label>
                            <label htmlFor="amount" className="label-prefix">$</label>
                            <input
                                id="amount"
                                type="text"
                                ref="amount"
                                placeholder="2,000"
                                className="with-prefix number"
                                />
                        </div>
                        <div className="half">
                            <label htmlFor="charity">Sent to:</label>
                            <select
                                id="charity"
                                ref="charity"
                                name="charity_id"
                            >
                                { this.state.options.map(o => {
                                    return (
                                        <option
                                            key={o.id}
                                            value={o.id}>
                                            { o.name }
                                        </option>
                                    )
                                }) }
                            </select>
                        </div>
                    </div>
                    <div className="container">
                        <div className="half">
                            <label htmlFor="name">My name is:</label>
                            <input
                                ref="name"
                                id="name"
                                name="campaigner_name"
                                type="text"
                                placeholder="Joseph Smith" />
                        </div>
                        <div className="half">
                            <label htmlFor="email">Keep me updated at:</label>
                            <input
                                ref="email"
                                id="email"
                                name="campaigner_email"
                                type="email"
                                placeholder="Email address" />
                        </div>
                    </div>
                    <button
                        onClick={ this.submitForm }>
                        Create campaign
                    </button>
                </form>
                <p className="centered small hidden">ps. <Link to="campaign">here's an example</Link>.</p>
                <p className="centered small"><Link to="about">about us</Link>.</p>
            </div>
        );
    }
}
