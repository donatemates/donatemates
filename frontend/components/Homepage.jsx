import React, { Component } from 'react';
import { Link } from 'react-router';

export default class Homepage extends Component {

    constructor(opts) {
        super(opts);

        this.state = {
            options: []
        }

        this.submitForm = this.submitForm.bind(this);
    }

    submitForm() {
        let campaign = {
            name: this.refs.name.value,
            amount: this.refs.amount.value,
            charity: this.refs.charity.value,
            email: this.refs.email.value
        };

        console.log(campaign)
    }

    componentDidMount() {
        // fetch('https://api.donatemates.com/charities').then(res => {
        //     if (res.ok) {
        //         res.json().then(availableCharities => {
        //             this.setState({
        //                 options: availableCharities
        //             })
        //         })
        //     }
        // });
        this.setState({
            options: [
                {
                    "donation_url": "https://action.aclu.org/donate-aclu?redirect=donate/join-renew-give",
                    "class": "ACLUParser",
                    "conversational_name": "the ACLU",
                    "id": "aclu",
                    "name": "ACLU"
                },
                {
                    "donation_url": "https://donate.doctorswithoutborders.org/onetime.cfm",
                    "class": "MSFParser",
                    "conversational_name": "Doctors Without Borders",
                    "id": "msf",
                    "name": "Doctors without Borders"
                },
                {
                    "donation_url": "https://secure.ppaction.org/site/Donation2?df_id=12913&12913.donation=form1",
                    "class": "PPParser",
                    "conversational_name": "Planned Parenthood",
                    "id": "pp",
                    "name": "Planned Parenthood"
                }
            ]
        })
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
                                placeholder="2,000"
                                className="with-prefix number"
                                />
                            <input
                                id="match_cents"
                                type="hidden"
                                name="match_cents"
                                ref="amount" />
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
