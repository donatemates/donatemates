import React, { Component } from 'react';
import { Router, Link } from 'react-router';

export default class About extends Component {

    render() {
        window.twttr = (function(d, s, id) {
            var js, fjs = d.getElementsByTagName(s)[0],
            t = window.twttr || {};
            if (d.getElementById(id)) return t;
            js = d.createElement(s);
            js.id = id;
            js.src = "https://platform.twitter.com/widgets.js";
            fjs.parentNode.insertBefore(js, fjs);

            t._e = [];
            t.ready = function(f) {
                t._e.push(f);
            };

            return t;
        }(document, "script", "twitter-wjs"));
        return (
            <div className="wrapper">
                <h1>donatemates</h1>
                <p><strong>{"Why?"}</strong></p>
                <p>
                    {"We built Donatemates because we wanted to make it easy for people to run matching campaigns with their friends and followers. Instead of using Google Sheets and carefully tracking @replies on Twitter, you can just check your email."}
                </p>
                <p><strong>{"Who's we?"}</strong></p>
                <p>
                    Donatemates is built by <a href="https://twitter.com/deankleissas">Dean</a>, <a href="https://twitter.com/j6m8">Jordan</a>, and <a href="https://twitter.com/shl">Sahil</a>. And you? We are <a href="https://github.com/donatemates/donatemates">open source</a>!
                </p>

                <p><strong>Where can I follow along?</strong></p>
                <p>Stay in the loop on updates and cool campaigns by clicking...</p>
                <p>
                    <a
                        className="twitter-follow-button"
                        href="https://twitter.com/donatemates">{"Follow @donatemates"}
                    </a>
                </p>
            </div>
        );
    }
}
