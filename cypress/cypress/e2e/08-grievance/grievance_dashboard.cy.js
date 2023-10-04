import GrievanceDashboard from "../../page-objects/pages/grievance/grievance_dashboard.po";

let grievanceDashboard = new GrievanceDashboard();

describe("Grievance Dashboard", () => {
  beforeEach(() => {
    cy.adminLogin();
    cy.navigateToHomePage();
    grievanceDashboard.clickMenuButtonGrievance();
    grievanceDashboard.clickMenuButtonGrievanceDashboard();
  });

  describe("Smoke tests Grievance Dashboard", () => {
    it("Check Grievance Dashboard page", () => {
      cy.scenario([
        "Go to Grievance page",
        "Go to Grievance Dashboard page",
        "Check if all elements on details page exist",
      ]);
      grievanceDashboard.checkElementsOnPage();
    });
  });

  describe("Component tests Grievance Dashboard", () => {
    context("Check numbers of tickets", () => {
      it.skip("ToDo", () => {});
    });
    context("Check number of closed tickets", () => {
      it.skip("ToDo", () => {});
    });
    context("Check average resolution", () => {
      it.skip("ToDo", () => {});
    });
  });
  describe.skip("E2E tests Grievance Dashboard", () => {});

  describe("Regression tests Grievance Dashboard", () => {
    it("174517: Check clear cash", () => {
      grievanceDashboard.clearCache();
      grievanceDashboard.checkElementsOnPage();
    });
  });
});
