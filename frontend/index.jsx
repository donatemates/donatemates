import React, {Component} from 'react';
import {render} from 'react-dom';
import { Router, Route, IndexRoute, Link, hashHistory } from 'react-router'

import css from './style.css';

import Homepage from './components/Homepage.jsx';
import About from './components/About.jsx';


class MainLayout extends Component {
    render() {
        return (
            <div>
                { this.props.children }
            </div>
        );
    }
}


const routes = {
    path: '/',
    component: MainLayout,
    indexRoute: { component: Homepage },
    childRoutes: [
        { path: 'about', component: About },
    //     { path: 'inbox', component: Inbox },
    ]
}

render(
    <Router history={hashHistory} routes={routes} />,
    document.getElementById('react-target')
);
