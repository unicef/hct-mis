import React from 'react';
import ReactDOM from 'react-dom';
import * as Sentry from '@sentry/react';
import ChartDataLabels from 'chartjs-plugin-datalabels';
import Chart from 'chart.js';
import setupInternalization from './i18n';
import { App } from './App';
import * as serviceWorker from './serviceWorker';

Chart.plugins.unregister(ChartDataLabels);
setupInternalization();
if (process.env.NODE_ENV !== 'development')
  Sentry.init({
    dsn: process.env.SENTRY_FRONTEND_DSN,
    ignoreErrors: ['Permission Denied'],
  });

ReactDOM.render(<App />, document.getElementById('root'));

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();
