// ***********************************************************
// This example plugins/index.js can be used to load plugins
//
// You can change the location of this file or turn off loading
// the plugins file with the 'pluginsFile' configuration option.
//
// You can read more here:
// https://on.cypress.io/plugins-guide
// ***********************************************************

// This function is called when a project is opened or re-opened (e.g. due to
// the project's config changing)

// https://gist.github.com/csuzw/845b589549b61d3a5fe18e49592e166f

const cucumber = require('cypress-cucumber-preprocessor').default;
const xlsx = require('xlsx');
// eslint-disable-next-line import/no-extraneous-dependencies
const browserify = require('@cypress/browserify-preprocessor');
const { AzureAdSingleSignOn } = require('./azure-ad-sso/plugin');

module.exports = (on) => {
  const options = browserify.defaultOptions;

  options.browserifyOptions.plugin.unshift([
    'tsify',
    { project: 'cypress/tsconfig.json' },
  ]);

  on('file:preprocessor', cucumber(options));
  on('task', {
    AzureAdSingleSignOn,

    parseXlsxData({ data, nameOrIndex }) {
      const workbook = xlsx.read(data, { type: 'binary' });

      const getJsonData = () => {
        const sheet =
          workbook.Sheets[
            typeof nameOrIndex === 'string' || nameOrIndex instanceof String
              ? nameOrIndex
              : workbook.SheetNames[nameOrIndex]
          ];

        return xlsx.utils.sheet_to_json(sheet);
      };

      return Promise.resolve({
        workbook,
        jsonData: nameOrIndex && getJsonData(),
      });
    },
  });
};
