import ProgramDetails from "../../page-objects/pages/program_details/program_details.po";
import ProgramManagement from "../../page-objects/pages/program_management/program_management.po";

let programDetails = new ProgramDetails();
let programManagement = new ProgramManagement();

describe("Program Details", () => {
  beforeEach(() => {
    cy.navigateToHomePage();
  });

  after(() => {
    cy.initScenario("init_clear");
    cy.adminLogin();
  });

  describe("Smoke tests Program Details", () => {
    it("Check Program Details page", () => {
      cy.scenario([
        "Go to Program Details page (Active program chosen)",
        "Check if all elements on page exist",
        "Change program to Draft program",
        "Check if all elements on page exist",
      ]);
      programDetails.getTableTitle().should("be.visible");
      programDetails.getTashPlanTableRow().should("have.length", 2);
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
      cy.scenario([
        "Go to Program Details page (Active program chosen)",
        "Press Finish Programme button",
        "Press Finish button on popup",
        "Check Status",
      ]);
      programDetails.getButtonFinishProgram().click();
      programDetails.getButtonFinishProgram().eq(1).click();
      programDetails.getStatusContainer().should("contain", "FINISHED");
    });
    it("Reactivate Program", () => {
      cy.scenario([
        "Go to Program Details page (Finished program chosen)",
        "Press Reactivate button",
        "Press Reactivate button on popup",
        "Check Status",
      ]);
      programDetails.getButtonDataCyButtonReactivateProgram().click();
      programDetails.getButtonDataCyButtonReactivateProgramPopup().click();
      programDetails.getStatusContainer().should("contain", "ACTIVE");
    });
    it.skip("Copy Program", () => {
      cy.scenario([
        "Go to Program Details page (Draft Program)",
        "Press Copy button",
        "Change Name",
        "Choose Data Collection Type",
        "Press Save",
        "Check if program created",
      ]);
      programDetails.navigateToProgrammePage("Draft Program");
      programDetails.getButtonCopyProgram().click();
      programManagement.getSelectDataCollectingTypeCode.click();
      programManagement.getInputDescription().clear().type("New Name");
      programManagement.getSelectOptionByName("Full");
      programManagement.getButtonSave().click();
      programDetails.getPageHeaderTitle().contains("New Name");
      programManagement
        .getPageHeaderTitle()
        .should("contain", "Programme Management");
    });
    it("Remove Program", () => {
      programDetails.navigateToProgrammePage("Draft Program");
      programDetails.getButtonRemoveProgram().click();
      programDetails.getButtonRemoveProgram().eq(1).click();
      programDetails.getGlobalProgramFilter().click();
      programDetails
        .getProgrammesOptions()
        .should("not.contain", "Draft Program");
      cy.initScenario("init_clear");
      cy.adminLogin();
    });
    it("Activate Program", () => {
      programDetails.navigateToProgrammePage("Draft Program");
      programDetails.getButtonActivateProgram().click();
      programDetails.getButtonActivateProgramModal().click();
      programDetails.getStatusContainer().should("contain", "ACTIVE");
    });
  });

  describe.skip("E2E tests Program Details", () => {});

  describe.skip("Regression tests Program Details", () => {});
});
