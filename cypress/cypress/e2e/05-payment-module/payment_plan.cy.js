import PaymentPlanPage from "../../page-objects/pages/payment_module/payment_plan_page.po";

let paymentPlanPage = new PaymentPlanPage();

describe("Payment Plan", () => {
  beforeEach(() => {
    cy.navigateToHomePage();
  });
  describe("Smoke tests Payment Plan module", () => {
    it.skip("Check Payment Plan page", () => {});
    it.skip("Check Payment Plan Details page", () => {});
  });
  describe("Component tests Payment Plan", () => {
    it("Can create a payment plan", () => {});
  });
  describe.skip("E2E tests Payment", () => {});

  describe.skip("Regression tests Payment", () => {});
});
