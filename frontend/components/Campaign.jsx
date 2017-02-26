import React, { Component } from 'react';

export default class Campaign extends Component {

    constructor(props) {
        super(props);

        this.state = {
        }
        this.formatCurrency = this.formatCurrency.bind(this);
    }

    formatCurrency(cents) {
        if (cents == 0) {
            return "$0";
        }
        var value = cents / 100;
        var num = '$' + value.toFixed(2).replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,");
        return num.replace(/\.00$/,'');
    }

    componentDidMount() {

        this.setState({
            campaigner_name: "Jordan",
            donation_email: "test@donatemates.com",
            large_donors: [],
            recent_donors: [],
            donation_total_cents: 100000,
            match_cents: 10000,
            donation_url: "example.com",
            charity_name: "Unplanned Parenthood",
        })
    }

    render() {
        return (
            <div className="wrapper" id="template-container">
                <span className="header-label centered" id="header-label">Contribute to</span>
                <h2 className="campaign-header centered">
                    { this.state.campaigner_name }&rsquo;s { this.formatCurrency(this.state.donation_total_cents) } matching campaign for { this.state.charity_name }
                </h2>
                <div className="progress-bar">
                    <div id="progress" className="progress"><strong data-content="matchedAmount">{ this.formatCurrency(this.state.match_cents) }</strong> (<span data-content="matchedPercentage">{ this.state.match_cents / this.state.donation_total_cents * 100 }%</span>)</div>
                </div>
                <div className="container" id="donor-container">
                    <div className="half">
                        <ul>
                            <li>
                                <strong>Most recent donors:</strong>
                            </li>
                            <div id="recent-donors">
                                { this.state.recent_donors }
                            </div>
                        </ul>
                    </div>
                    <div className="half">
                        <ul>
                            <li>
                                <strong>Top donors:</strong>
                            </li>
                            <div id="large-donors">
                                { this.state.large_donors }
                            </div>
                        </ul>
                    </div>
                </div>
                <hr />
                <p id="active-notice" className="centered">
                    Donate by clicking <a href={ this.state.donation_url } id="donation-link">here</a>, forward the receipt email to <span data-content="donationEmail">{ this.state.donation_email }</span>, and it'll show up here.
                </p>
                <p className="footer centered">powered by</p>
                <a href="/"><h1>donatemates</h1></a>
            </div>
        );
    }
}
