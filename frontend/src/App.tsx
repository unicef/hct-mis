import React from 'react';
import {Dialog, Snackbar, SnackbarContent, ThemeProvider} from '@material-ui/core';
import { ThemeProvider as StyledThemeProvider } from 'styled-components';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import CssBaseline from '@material-ui/core/CssBaseline';
import { MuiPickersUtilsProvider } from '@material-ui/pickers';
import moment from 'moment';
import MomentUtils from '@date-io/moment';
import { ApolloProvider } from '@apollo/react-hooks';
import { theme } from './theme';
import { HomeRouter } from './containers/HomeRouter';
import { ProfilePage } from './containers/pages/ProfilePage';
import { client } from './apollo/client';
import { LoginPage } from './containers/pages/LoginPage';
import { DefaultRoute } from './containers/DefaultRoute';
import {useSnackbar} from "./hooks/useSnackBar";

export const App: React.FC = () => {
  return (
    <ApolloProvider client={client}>
      <ThemeProvider theme={theme}>
        <StyledThemeProvider theme={theme}>
          <MuiPickersUtilsProvider libInstance={moment} utils={MomentUtils}>
            <CssBaseline />
            <Router>
              <Switch>
                <Route path='/login'>
                  <LoginPage />
                </Route>
                <Route path='/accounts/profile/'>
                  <ProfilePage />
                </Route>
                <Route path='/:businessArea/'>
                  <HomeRouter />
                </Route>
                <Route path='/'>
                  <DefaultRoute />
                </Route>
              </Switch>
            </Router>
          </MuiPickersUtilsProvider>
        </StyledThemeProvider>
      </ThemeProvider>
    </ApolloProvider>
  );
};
