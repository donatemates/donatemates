import React, { Component } from 'react';
import browserHistory from 'react-router/lib/browserHistory';
import NotFound from './NotFound.jsx';

import Loading from './Loading.jsx';

import utils from '../utils.js';
import rootUrl from '../endpoint.js';


class DonorRow extends Component {
    render() {
        return (
            <li>{ utils.formatCurrency(this.props.amount) } from {this.props.name}</li>
        );
    }
}


export default class Campaign extends Component {

    constructor(props) {
        super(props);

        this.state = {
            large_donors: [],
            recent_donors: [],
        }

        this.refresh = this.refresh.bind(this);
    }

    refresh() {
        fetch(`${ rootUrl }campaign/${this.props.params.campaign_id}`).then(res => {
            if (res.ok) {
                res.json().then(json => {
                    this.setState({
                        campaign_id: json.campaign_id,
                        charity_name: json.charity_name,
                        secret_id: json.secret_id,
                        created_on: json.created_on,
                        notified_on: json.notified_on,
                        campaigner_email: json.campaigner_email,
                        campaigner_name: json.campaigner_name,
                        campaign_status: json.campaign_status,
                        donation_total_cents: json.donation_total_cents,
                        match_cents: json.match_cents,
                        donation_url: json.donation_url,
                        donation_email: json.donation_email,
                        charity_id: json.charity_id,
                        recent_donors: json.recent_donors.map(donor => [donor.donation_cents, donor.donor_name]),
                        large_donors: json.large_donors.map(donor => [donor.donation_cents, donor.donor_name]),
                    });
                })
            } else {
                this.setState({ notFound: true })
            }
        });
    }

    componentDidMount() {
        window.setInterval(this.refresh, 30 * 1000);
        this.refresh();
    }

    render() {
        if (this.state.notFound) {
            return <NotFound />
        }
        if (!this.state.donation_url) {
            return (<Loading />);
        }

        let headerText, titleText, footerText;

        titleText = [this.state.campaigner_name, "'s ", utils.formatCurrency(this.state.match_cents), " matching campaign for ", this.state.charity_name].join('');

        if (this.state.campaign_status != "active") {
            headerText = this.state.campaign_status;
            footerText = "";
        } else {
            headerText = "Contribute to"
            footerText = (
                <p className="centered">
                    Donate by clicking <a href={ this.state.donation_url }>here</a>, forward the receipt email to <span data-content="donationEmail">{ this.state.donation_email }</span>, and it'll show up here.
                </p>
            );
        }

        let donorSection;
        if (this.state.recent_donors.length > 0) {
            donorSection = (
                <div className="container" id="donor-container">
                    <div className="half">
                        <ul>
                            <li>
                                <strong>Most recent donors:</strong>
                            </li>
                            <div id="recent-donors">
                                { this.state.recent_donors.map(donor => {
                                    return (
                                        <DonorRow name={donor[1]} amount={donor[0]} />
                                    );
                                }) }
                            </div>
                        </ul>
                    </div>
                    <div className="half">
                        <ul>
                            <li>
                                <strong>Top donors:</strong>
                            </li>
                            <div id="large-donors">
                                { this.state.large_donors.map(donor => {
                                    return (
                                        <DonorRow name={donor[1]} amount={donor[0]} />
                                    );
                                }) }
                            </div>
                        </ul>
                    </div>
                </div>
            );
        } else {
            donorSection = (<div></div>);
        }

        return (
            <div className="wrapper" id="template-container">
                <span className="header-label centered" id="header-label">{ headerText }</span>
                <h2 className="campaign-header centered">
                    { titleText }
                </h2>
                <div className="progress-bar">
                    <div
                        id="progress"
                        className="progress"
                        style={{
                            minWidth: Math.round(this.state.donation_total_cents / this.state.match_cents * 100) + "%"
                        }}>
                        <strong data-content="matchedAmount">
                            { utils.formatCurrency(this.state.donation_total_cents) }
                        </strong>&nbsp;
                        (<span data-content="matchedPercentage">
                            {
                                Math.round(this.state.donation_total_cents / this.state.match_cents * 100)
                            }
                        %</span>)
                    </div>
                </div>

                { donorSection }

                <hr />
                { footerText }
                <p className="footer centered">powered by</p>
                <a href="/"><h1>donatemates</h1></a>
            </div>
        );
    }
}
