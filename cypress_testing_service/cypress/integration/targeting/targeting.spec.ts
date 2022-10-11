import { When, Then, Given } from 'cypress-cucumber-preprocessor/steps';
import {
  fillTargetingForm,
  uniqueSeed,
} from '../../procedures/procedures';

let individualIds = [];
let programName = "TargetingProgram"

Given('I am authenticated', () => {
  cy.visit('/api/unicorn/');
  cy.get('input[name="username"]').type(Cypress.env('daUsername'));
  cy.get('input[name="password"]').type(Cypress.env('daPassword'));
  cy.get('input').contains('Log in').click();
});

When('I visit the main dashboard', () => {
  cy.visit('/');
});

Then('I should see the side panel with Targeting option', () => {
  cy.get('span').contains('Targeting');
});

When('I click on Targeting option', () => {
  cy.get('span').contains('Targeting').click();
});

Then('I should see the Targeting page', () => {
  cy.get('h5').contains('Targeting');
});

When('I click the Create New button', () => {
  cy.get('[data-cy="button-target-population-create-new"]').click({
    force: true,
  });
});

Then('I should see the Create Target Population page', () => {
  cy.get('[data-cy="input-name"]')
    .first()
    .find('label')
    .contains('Enter Target Population Name');
});

When('I fill out the form fields and save', () => {
  fillTargetingForm(cy, programName, "TargetingVille");
  cy.get('[data-cy="button-target-population-add-criteria"]').eq(1).click();
});

Then('I should see the Households table', () => {
  cy.get('h6').contains('Households');
});

When('I save the Target Population', () => {
  cy.get(
    '[data-cy=button-target-population-create] > .MuiButton-label',
  ).click();
});

Then('I should see the Target Population details page and status Open', () => {
  cy.get('h6').contains('Targeting Criteria');
  cy.get('[data-cy="status-container"]').contains('Open');
});

When('I Lock Target Population', () => {
  cy.get('[data-cy="button-target-population-lock"]').click({ force: true });
  cy.get('[data-cy="button-target-population-modal-lock"]').click({
    force: true,
  });
});

Then(
  'I should see the Target Population details page and status Locked',
  () => {
    cy.get('h6').contains('Targeting Criteria');
    cy.get('[data-cy="status-container"]').contains('Locked');
  },
);

When('I Send Target Population to HOPE', () => {
  cy.get('[data-cy="button-target-population-send-to-hope"]').click({
    force: true,
  });
  cy.get('[data-cy="button-target-population-modal-send-to-hope"]').click();
});

Then('I should see the Target Population details page and status Ready', () => {
  cy.get('h6').contains('Targeting Criteria');
  cy.get('[data-cy="status-container"]').contains('Ready');
});
