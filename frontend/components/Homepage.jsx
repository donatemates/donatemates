import React, { Component } from 'react';

export default class Homepage extends Component {
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
                            <input id="amount" type="text" placeholder="2,000" className="with-prefix number" />
                            <input id="match_cents" type="hidden" name="match_cents" />
                        </div>
                        <div className="half">
                            <label htmlFor="charity">Sent to:</label>
                            <select id="charity" name="charity_id">
                                <option>Loading...</option>
                            </select>
                        </div>
                    </div>
                    <div className="container">
                        <div className="half">
                            <label htmlFor="name">My name is:</label>
                            <input id="name" name="campaigner_name" type="text" placeholder="Joseph Smith" />
                        </div>
                        <div className="half">
                            <label htmlFor="email">Keep me updated at:</label>
                            <input id="email" name="campaigner_email" type="email" placeholder="Email address" />
                        </div>
                    </div>
                    <button type="submit" className="js-create-campaign-trigger">Create campaign</button>
                </form>
                <p className="centered small hidden">ps. <a href="campaign.html">here's an example</a>.</p>
                <p className="centered small"><a href="about.html">about us</a>.</p>
            </div>
        );
    }
}
