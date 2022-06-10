import MomentUtils from '@date-io/moment';
import { ThemeProvider } from '@mui/material';
import CssBaseline from '@mui/material/CssBaseline';
import { MuiPickersUtilsProvider } from '@mui/pickers';
import moment from 'moment';
import React from 'react';
import { ThemeProvider as StyledThemeProvider } from 'styled-components';
import { theme } from '../theme';

export const TestProviders: React.FC = ({ children }) => (
  <ThemeProvider theme={theme}>
    <StyledThemeProvider theme={theme}>
      <MuiPickersUtilsProvider libInstance={moment} utils={MomentUtils}>
        <CssBaseline />
        {children}
      </MuiPickersUtilsProvider>
    </StyledThemeProvider>
  </ThemeProvider>
);
