// ***********************************************************
// This example support/index.js is processed and
// loaded automatically before your test files.
//
// This is a great place to put global configuration and
// behavior that modifies Cypress.
//
// You can change the location of this file or turn off
// automatically serving support files with the
// 'supportFile' configuration option.
//
// You can read more here:
// https://on.cypress.io/configuration
// ***********************************************************

// Import commands.js using ES2015 syntax:
import 'cypress-promise/register';
import 'cypress-file-upload';
import './commands';
import './chai';

// TODO remove if no optimization gain
// Cypress.Cookies.defaults({
//   whitelist: [
//     ...mockAuthCookies.map(({ name }) => name),
//   ],
// });
