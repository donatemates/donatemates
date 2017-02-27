import React, {Component} from 'react';
import {render} from 'react-dom';
import { Router, Route, IndexRoute, Link, browserHistory } from 'react-router'

import css from './style.less';

import Homepage from './components/Homepage.jsx';
import About from './components/About.jsx';
import Cancel from './components/Cancel.jsx';
import Campaign from './components/Campaign.jsx';
import NotFound from './components/NotFound.jsx';


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
        { path: 'campaign/:campaign_id', component: Campaign },
        { path: 'cancel/:campaign_id/:secret', component: Cancel },
        { path: '*', component: NotFound },
    //     { path: 'inbox', component: Inbox },
    ]
}

render(
    <Router history={browserHistory} routes={routes} />,
    document.getElementById('react-target')
);
