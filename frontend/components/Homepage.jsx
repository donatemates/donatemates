import React, { Component } from 'react';
import Link from 'react-router/lib/Link';
import browserHistory from 'react-router/lib/browserHistory';
import Loading from './Loading.jsx';

import rootUrl from '../endpoint.js';


let isValidEmail = function(val) {
    return (/^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/.test(val))
};


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

        // Check each input box for a value. Error if none.
        const inputs = ['name', 'amount', 'charity', 'email'];
        const inputChecks = {
            'name': val => (!!val),
            'amount': val => (!!val && !isNaN(val)),
            'charity': val => (!!val),
            'email': val => (!!val && isValidEmail(val))
        };
        let foundError = false;
        inputs.forEach(i => {
            this.refs[i].classList.remove('error');
            if (!inputChecks[i](this.refs[i].value)) {
                this.refs[i].classList.add('error');
                foundError = true;
            }
        });
        if (foundError) {
            return;
        }
        return;

        let campaign = {
            charity_id: this.refs.charity.value,
            campaigner_name: this.refs.name.value,
            match_cents: parseFloat(this.refs.amount.value) * 100,
            campaigner_email: this.refs.email.value
        };


        var query = "";
        for (let key in campaign) {
            query += encodeURIComponent(key)+"="+encodeURIComponent(campaign[key])+"&";
        }
        fetch(`${ rootUrl }campaign/?${query}`, {
            method: "POST"
        }).then(res => {
            res.json().then(json => {
                browserHistory.push('/campaign/' + json.campaign_id);
            })
        });
        this.setState({
            submitted: true
        })
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
        if (this.state.submitted) {
            return (<Loading />);
        }
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
                                onChange={ (ev) => {
                                    ev.target.classList.remove('error');
                                    if (isNaN(ev.target.value)) {
                                        ev.target.classList.add('error');
                                    }
                                }}
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
                                placeholder="Email address"
                                onChange={ (ev) => {
                                    ev.target.classList.remove('error');

                                    if (!isValidEmail(ev.target.value)) {
                                        ev.target.classList.add('error');
                                    }
                                }}
                                />
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
