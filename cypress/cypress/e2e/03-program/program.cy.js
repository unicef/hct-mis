/// <reference types="cypress" />
context("Program", () => {
  beforeEach(() => {
    cy.adminLogin()
    cy.visit("/");
    cy.get("span").contains("Programme Management").click();
  });
  it("Create a program", () => {
    cy.get("h5").should('contain', "Programme Management");
    cy.get('[data-cy="button-new-program"]').click({ force: true });
    cy.get("h6").should('contain', "Set-up a new Programme");
    cy.uniqueSeed().then((seed) => {
      const programName = `test program ${seed}`;
      cy.get('[data-cy="input-programme-name"]').type(programName);
      cy.get('[data-cy="input-cash-assist-scope"]').first().click();
      cy.get('[data-cy="select-option-Unicef"]').click();
      cy.get('[data-cy="input-sector"]').first().click();
      cy.get('[data-cy="select-option-Multi Purpose"]').click();
      cy.get('[data-cy="input-start-date"]').click().type("2023-01-01");
      cy.get('[data-cy="input-end-date"]').click().type("2033-12-30");
      cy.get('[data-cy="input-description"]')
        .first()
        .click()
        .type("test description");
      cy.get('[data-cy="input-budget"]')
        .first()
        .click()
        .type("{backspace}{backspace}{backspace}{backspace}9999");
      cy.get('[data-cy="input-admin-area"]').click().type("Some Admin Area");
      cy.get('[data-cy="input-population-goal"]')
        .click()
        .type("{backspace}{backspace}{backspace}{backspace}4000");
      cy.get('[data-cy="button-save"]').click({ force: true });
      cy.get("h6").should('contain', "Programme Details");
      cy.get('[data-cy="button-activate-program"]').click({ force: true });
      cy.get('[data-cy="button-activate-program-modal"]').click({ force: true });
      cy.get('[data-cy="status-container"]').should('contain', "ACTIVE");
    });
  });
  it("Edit Program", () => {
    cy.get('[data-mui-test="SelectDisplay"]').eq(0).click({ force: true })
    cy.get('[data-value="ACTIVE"]').click({ force: true })
    cy.get('[data-cy="status-container"]').should('contain', 'ACTIVE')
    cy.get('[data-cy="status-container"]').eq(0).click({ force: true })
    cy.contains('EDIT PROGRAMME').click({ force: true })
    cy.uniqueSeed().then((seed) => {
      const editedProgramName = `Edited program ${seed}`;
      cy.get('[data-cy="input-programme-name"]').clear().type(editedProgramName);
      cy.get('[data-cy="input-cash-assist-scope"]').first().click();
      cy.get('[data-cy="select-option-Unicef"]').click();
      cy.get('[data-cy="input-sector"]').first().click();
      cy.get('[data-cy="select-option-Multi Purpose"]').click();
      cy.get('[data-cy="input-start-date"]').click().type("2023-01-10");
      cy.get('[data-cy="input-end-date"]').click().type("2033-12-31");
      cy.get('[data-cy="input-description"]')
        .first().clear().type("Edit Test description");
      cy.get('[data-cy="input-budget"]')
        .first()
        .click()
        .type("{backspace}{backspace}{backspace}{backspace}8888");
      cy.get('[data-cy="input-admin-area"]').clear().type("Some Admin Area");
      cy.get('[data-cy="input-population-goal"]')
        .click()
        .type("{backspace}{backspace}{backspace}{backspace}2000");
      cy.get('[data-cy="button-save"]').click({ force: true });
      cy.get("h5").should('contain', editedProgramName);
    })
  })
  it("Finish Program", () => {
    cy.get('[data-mui-test="SelectDisplay"]').eq(0).click({ force: true })
    cy.get('[data-value="ACTIVE"]').click({ force: true })
    cy.reload()
    cy.get('[data-cy="status-container"]').should('contain', 'ACTIVE')
    cy.get('[data-cy="status-container"]').eq(0).click({ force: true })
    cy.contains('Finish Programme').click({ force: true })
    cy.get('[data-cy="button-finish-program"]').eq(1).click({ force: true })
    cy.get('[data-cy="status-container"]').should('contain', "FINISHED");
  })
  it("Reactivate Program", () => {
    cy.get('[data-mui-test="SelectDisplay"]').eq(0).click({ force: true })
    cy.get('[data-value="FINISHED"]').click({ force: true })
    cy.reload()
    cy.get('[data-cy="status-container"]').should('contain', "FINISHED");
    cy.get('[data-cy="status-container"]').eq(0).click({ force: true })
    cy.contains('Reactivate').eq(0).click({ force: true })
    cy.get('.MuiDialogActions-root > .MuiButton-contained').click({ force: true })
    cy.get('[data-cy="status-container"]').should('contain', "ACTIVE");
  })
})

