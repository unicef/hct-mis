import { When, Then, Given, And } from 'cypress-cucumber-preprocessor/steps';
import { uniqueSeed } from '../../procedures/procedures';

let targetPopulationName = 'PaymentPlanTargetPopulation';
let paymentPlanUnicefId;
let fspXlsxFilenames;
const downloadsFolder = Cypress.config('downloadsFolder');

const fileName = (id) => `payment_plan_payment_list_${id}`;

const xlsxFileName = (id) => `${fileName(id)}.xlsx`;
const zipFileName = (id) => `${fileName(id)}.zip`;

Given('I am authenticated', () => {
  cy.visit('/api/unicorn/');
  cy.get('input[name="username"]').type(Cypress.env('daUsername'));
  cy.get('input[name="password"]').type(Cypress.env('daPassword'));
  cy.get('input').contains('Log in').click();
});

Given('I initialize the data', () => {
  cy.exec(`yarn init-scenario payment_plan/${uniqueSeed}`);
});

Given('Business area is payment plan applicable', () => {
  cy.visit('/api/unicorn/core/businessarea/');
  cy.get('th').contains('Afghanistan').parent().find('a').click();
  cy.get('#id_is_payment_plan_applicable').should('be.checked');
});

When('I visit the main dashboard', () => {
  cy.visit('/');
});

Then('I should see the side panel with Payment Module option', () => {
  cy.get('span').contains('Payment Module');
});

When('I click on Payment Module option', () => {
  cy.get('span').contains('Payment Module').click();
  cy.wait(1000); // eslint-disable-line cypress/no-unnecessary-waiting
});

Then('I should see the Payment Module page', () => {
  cy.get('[data-cy="page-header-container"]').contains('Payment Module');
});

When('I click the New Payment Plan button', () => {
  cy.get('[data-cy="button-new-payment-plan"]').click({
    force: true,
  });
});

Then('I should see the New Payment Plan page', () => {
  cy.get('[data-cy="page-header-container"]').contains('New Payment Plan');
});

When('I fill out the form fields and save', () => {
  cy.get('[data-cy="input-target-population"]').first().click();
  cy.wait(200); // eslint-disable-line cypress/no-unnecessary-waiting
  cy.get(
    `[data-cy="select-option-${targetPopulationName}-${uniqueSeed}"]`,
  ).click();

  cy.get('[data-cy="input-start-date"]').click().type('2022-12-12');
  cy.get('[data-cy="input-end-date"]').click().type('2022-12-23');
  cy.get('[data-cy="input-currency"]').first().click();
  cy.get('[data-cy="select-option-Afghan afghani"]').click();
  cy.get('[data-cy="input-dispersion-start-date"]').click().type('2023-12-12');
  cy.get('[data-cy="input-dispersion-end-date"]').click().type('2023-12-23');
  cy.get('[data-cy="button-save-payment-plan"]').click({
    force: true,
  });
  cy.wait(3000); // eslint-disable-line cypress/no-unnecessary-waiting
});

Then('I should see the Payment Plan details page', () => {
  cy.get('[data-cy="page-header-container"]').contains('Payment Plan ID', {
    timeout: 10000,
  });
  cy.get('[data-cy="pp-unicef-id"]').then(($el) => {
    paymentPlanUnicefId = $el.text();
  });
  cy.get('h6').contains('Details');
  cy.get('h6').contains('Results');
  cy.get('h6').contains('Payments List');
  cy.get('h6').contains('Activity Log');
});

When('I lock the Payment Plan', () => {
  cy.get('[data-cy="button-lock-plan"]').click({
    force: true,
  });
  cy.get('[data-cy="button-submit"]').click({
    force: true,
  });
});

Then('I see the entitlements input', () => {
  cy.get('[data-cy=input-entitlement-formula]').should('exist');
});

When('I choose the steficon rule', () => {
  cy.get('[data-cy=input-entitlement-formula] > .MuiSelect-root').click({
    force: true,
  });
  cy.get('[data-cy="input-entitlement-formula"]').click({ force: true });
  cy.get('li').contains(`Rule-${uniqueSeed}`).click({ force: true });
});

And('I apply the steficon rule', () => {
  cy.get('[data-cy="button-apply-steficon"]').click({ force: true });
  cy.reload();
});

Then('I see the entitlements calculated', () => {
  cy.get('[data-cy="total-entitled-quantity-usd"]').contains('USD');
  // TODO: check the amount
});

When('I click Set up FSP button', () => {
  cy.get('[data-cy="button-set-up-fsp"]').click({ force: true });
});

Then('I should see the Set up FSP page', () => {
  cy.get('[data-cy="page-header-container"]').contains('Set up FSP', {
    timeout: 10000,
  });
});

When('I select the delivery mechanisms', () => {
  cy.get('[data-cy="select-deliveryMechanisms[0].deliveryMechanism"]').click();
  cy.get('[data-cy="select-option-Transfer"]').click();
  cy.get('[data-cy="button-next-save"]').click({ force: true });
});

Then('I should be able to assign FSPs', () => {
  cy.get('[data-cy="select-deliveryMechanisms[0].fsp"]');
});

When('I select the FSPs and save', () => {
  cy.get('[data-cy="select-deliveryMechanisms[0].fsp"]').click();
  cy.get('[data-cy="select-option-Test FSP Transfer"]').click();
  cy.get('[data-cy="button-next-save"]').click({ force: true });
});

Then('I should see volumes by delivery mechanisms', () => {
  cy.contains('Volume by Delivery Mechanism in USD');
});

When('I lock the FSPs', () => {
  cy.get("[data-cy='button-lock-plan']").click({ force: true });
  cy.get("[data-cy='button-submit']").click({ force: true });
});

Then('I should see that the status is FSP Locked', () => {
  cy.get("[data-cy='status-container']").contains('FSP Locked');
});

When('I send the Payment Plan for approval', () => {
  cy.get("[data-cy='button-send-for-approval']").click({ force: true });
});

Then('I see the acceptance process stepper', () => {
  cy.contains('Acceptance Process');
});

When('I approve the Payment Plan', () => {
  cy.get("[data-cy='button-approve']").click({ force: true });
  cy.get("[data-cy='button-submit']").click({ force: true });
});

Then('I see the Payment Plan as in authorization', () => {
  cy.get('[data-cy="status-container"]').contains('In Authorization');
});

When('I authorize the Payment Plan', () => {
  cy.get("[data-cy='button-authorize']").click({ force: true });
  cy.get("[data-cy='button-submit']").click({ force: true });
});

Then('I see the Payment Plan as in review', () => {
  cy.get('[data-cy="status-container"]').contains('In Review');
});

When('I finalize the Payment Plan', () => {
  cy.get("[data-cy='button-mark-as-reviewed']").click({ force: true });
  cy.get("[data-cy='button-submit']").click({ force: true });
});

Then('I see the Payment Plan as accepted', () => {
  cy.get('[data-cy="status-container"]').contains('Accepted');
});

When('I download the xlsx template', () => {
  cy.get('[data-cy="button-export-xlsx"]').click({ force: true });
  cy.wait(1000); // eslint-disable-line cypress/no-unnecessary-waiting
  cy.reload();

  cy.get('[data-cy="button-download-template"]').click({ force: true });
});

Then('I fill the xlsx template', () => {
  // Wait for the file to be generated
  cy.wait(1000); // eslint-disable-line cypress/no-unnecessary-waiting
  const name = xlsxFileName(paymentPlanUnicefId);
  const downloadedFilePath = `${downloadsFolder}/${name}`;
  cy.exec(`node cypress/scripts/fillXlsxEntitlements.js ${downloadedFilePath}`);
});

When('I upload the xlsx template', () => {
  const name = xlsxFileName(paymentPlanUnicefId);
  const filledFilePath = `out_${name}`;
  cy.log(filledFilePath);
  cy.get('[data-cy="button-import"]').click({ force: true });
  cy.fixture(filledFilePath, 'base64').then((fileContent) => {
    cy.get('[data-cy="file-input"]').upload({
      fileContent,
      fileName: name,
      mimeType:
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      encoding: 'base64',
    });
  });
  cy.get('[data-cy="button-import-entitlement"').click({ force: true });
  cy.wait(2000); // eslint-disable-line cypress/no-unnecessary-waiting
  cy.reload();
});

And('I see that all individuals have proper payment channels', () => {
  cy.get('td').should('not.contain', 'Missing');
});

And('I export xlsx to zip file', () => {
  cy.get('[data-cy="button-export-xlsx"]').click({ force: true });
  cy.wait(500); // eslint-disable-line cypress/no-unnecessary-waiting
  cy.reload();
  cy.get('[data-cy="button-download-xlsx"]').click({ force: true });
  cy.wait(500); // eslint-disable-line cypress/no-unnecessary-waiting
});

When('I unarchive the zip file', () => {
  const name = zipFileName(paymentPlanUnicefId);
  const downloadedFilePath = `${downloadsFolder}/${name}`;
  cy.log(`Unzipping ${downloadedFilePath} to ${downloadsFolder}`);
  cy.exec(`unzip ${downloadedFilePath} -d ${downloadsFolder}`);
});

Then('I see the {int} xlsx files', (count) => {
  const currentRunFileName = fileName(paymentPlanUnicefId);
  cy.exec(
    `find ${downloadsFolder} | grep ${currentRunFileName} | grep FSP | sed 's@.*/@@'`,
  ).then((result) => {
    fspXlsxFilenames = result.stdout.split('\n');
    cy.log(fspXlsxFilenames);
    expect(fspXlsxFilenames.length).to.eq(count);
  });
});

When('I fill the reconciliation info', () => {
  const fspFilename = fspXlsxFilenames[0];
  cy.log(downloadsFolder);
  const downloadedFilePath = `${downloadsFolder}/${fspFilename}`;
  cy.log(downloadedFilePath);
  cy.exec(
    `node cypress/scripts/fillXlsxReconciliation.js "${downloadedFilePath}"`,
  );
});

And('I upload the reconciliation info', () => {
  const fspFilename = fspXlsxFilenames[0];

  const filledFilePath = `out_${fspFilename}`;
  cy.log(filledFilePath);
  cy.get('[data-cy="button-import"]').click({ force: true });
  cy.fixture(filledFilePath, 'base64').then((fileContent) => {
    cy.get('[data-cy="file-input"]').upload({
      fileContent,
      fileName: fspFilename,
      mimeType:
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      encoding: 'base64',
    });
  });
  cy.get('[data-cy="file-input"').click({ force: true });
  // cy.get('[data-cy="imported-file-name"]').should('exist'); // TODO
  cy.get('[data-cy="button-import-submit"').click({ force: true });
  cy.wait(500); // eslint-disable-line cypress/no-unnecessary-waiting
  cy.reload();
});

Then('I see the delivered quantities for each payment', () => {
  cy.get('[data-cy="delivered-quantity-cell"]').each(($el) => {
    cy.wrap($el).should('contain', 'AFN');
    cy.wrap($el).should('contain', '100');
  });
});
