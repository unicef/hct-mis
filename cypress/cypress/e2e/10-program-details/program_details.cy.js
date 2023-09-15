import ProgramDetails from "../../page-objects/pages/program_details/program_details.po";

let programDetails = new ProgramDetails();

describe("Program Details", () => {
  beforeEach(() => {
    cy.navigateToHomePage();
  });

  describe("Smoke tests Program Details", () => {
    it("Check Program Details page", () => {
      cy.scenario([
        "1. Go to Program Details page (Active program chosen)",
        "2. Check if all elements on page exist",
        "3. Change program to Draft program",
        "4. Check if all elements on page exist",
      ]);
      programDetails.getTableTitle().should("be.visible");
      programDetails.getTashPlanTableRow().should("have.length", 1);
      programDetails.getLabelAdministrativeAreasOfImplementation();
      programDetails.getButtonEditProgram().should("be.visible");
      programDetails.getLabelTotalNumberOfHouseholds().should("be.visible");
      programDetails.getLabelIndividualsData().should("be.visible");
      programDetails.getLabelCASH().should("be.visible");
      programDetails.getLabelDescription().should("be.visible");
      programDetails.getLabelFrequencyOfPayment().should("be.visible");
      programDetails.getLabelScope().should("be.visible");
      programDetails.getLabelSector().should("be.visible");
      programDetails.getLabelENDDATE().should("be.visible");
      programDetails.getLabelSTARTDATE().should("be.visible");
      programDetails.getStatusContainer().should("be.visible");
      programDetails.getLabelStatus().should("be.visible");
      programDetails.getPageHeaderTitle().should("be.visible");
      programDetails.getTablePagination().should("be.visible");
      programDetails.getTableLabel().should("be.visible");
      programDetails.getButtonCopyProgram().should("be.visible");

      programDetails.getGlobalProgramFilter().click();
      programDetails
        .getProgrammesOptions()
        .contains(programDetails.textDraftProgram)
        .click();

      programDetails.getButtonActivateProgram().should("be.visible");
      programDetails.getButtonRemoveProgram().should("be.visible");

      programDetails
        .getLabelAdministrativeAreasOfImplementation()
        .should("be.visible");
      programDetails.getButtonEditProgram().should("be.visible");
      programDetails.getLabelTotalNumberOfHouseholds().should("be.visible");
      programDetails.getLabelIndividualsData().should("be.visible");
      programDetails.getLabelCASH().should("be.visible");
      programDetails.getLabelDescription().should("be.visible");
      programDetails.getLabelFrequencyOfPayment().should("be.visible");
      programDetails.getLabelScope().should("be.visible");
      programDetails.getLabelSector().should("be.visible");
      programDetails.getLabelENDDATE().should("be.visible");
      programDetails.getLabelSTARTDATE().should("be.visible");
      programDetails.getStatusContainer().should("be.visible");
      programDetails.getLabelStatus().should("be.visible");
      programDetails.getPageHeaderTitle().should("be.visible");
      programDetails.getButtonCopyProgram().should("be.visible");
      programDetails.getTablePagination().should("not.exist");
      programDetails.getTableLabel().should("not.exist");
      programDetails.getTableTitle().should("not.exist");
      programDetails.getTashPlanTableRow().should("not.exist");
    });
  });

  describe("Component tests Program Details", () => {
    it("Finish Program", () => {
      cy.get('[data-mui-test="SelectDisplay"]').eq(0).click({ force: true });
      // cy.get('[data-value="ACTIVE"]').click({ force: true });
      // cy.get('[data-cy="button-filters-apply"]').click();
      // cy.reload();
      // cy.get('[data-cy="status-container"]').should("contain", "ACTIVE");
      // cy.get('[data-cy="status-container"]').eq(0).click({ force: true });
      // cy.contains("Finish Programme").click({ force: true });
      // cy.get('[data-cy="button-finish-program"]').eq(1).click({ force: true });
      // cy.get('[data-cy="status-container"]').should("contain", "FINISHED");
    });
    it("Reactivate Program", () => {
      cy.get('[data-mui-test="SelectDisplay"]').eq(0).click({ force: true });
      cy.get('[data-value="FINISHED"]').click({ force: true });
      cy.get('[data-cy="button-filters-apply"]').click();
      cy.reload();
      cy.get('[data-cy="status-container"]').should("contain", "FINISHED");
      cy.get('[data-cy="status-container"]').eq(0).click({ force: true });
      cy.contains("Reactivate").eq(0).click({ force: true });
      cy.get(".MuiDialogActions-root > .MuiButton-contained").click({
        force: true,
      });
      cy.get('[data-cy="status-container"]').should("contain", "ACTIVE");
    });
    it.skip("Remove Program", () => {});
    it.skip("Activate Program", () => {});
    it.skip("Reactivate Program", () => {});
  });

  describe.skip("E2E tests Program Details", () => {});

  describe.skip("Regression tests Program Details", () => {});
});
