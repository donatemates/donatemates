import React, {Component} from 'react';
import {render} from 'react-dom';
import css from './style.css';

import Homepage from './components/Homepage.jsx';


render(
    <Homepage />,
    document.getElementById('react-target')
);
