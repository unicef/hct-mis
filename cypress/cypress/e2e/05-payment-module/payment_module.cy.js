import PaymentModule from "../../page-objects/pages/payment_module/payment_module.po";
import PMDetailsPage from "../../page-objects/pages/payment_module/details_page.po";
import NewPaymentPlan from "../../page-objects/pages/payment_module/new_payment_plan.po";

let paymentModule = new PaymentModule();
let pmDetailsPage = new PMDetailsPage();
let newPaymentPlan = new NewPaymentPlan();

describe("Payment Module", () => {
  before(() => {
    cy.initScenario("payment_plan");
  });
  beforeEach(() => {
    cy.navigateToHomePage();
    cy.visit("/api/unicorn/core/businessarea/");
    cy.get("th").contains("Afghanistan").parent().find("a").click();
    cy.get("#id_is_payment_plan_applicable").should("be.checked");
  });
  describe("Smoke tests Payment module", () => {
    it.skip("Check Payment page", () => {});
    it.skip("Check Payment Details page", () => {});
    it.skip("Check Payment New Ticket page", () => {});
  });
  describe("Component tests Payment", () => {
    it("Can create a payment plan", () => {
      const downloadsFolder = Cypress.config("downloadsFolder");
      const fileName = (id) => `payment_plan_payment_list_${id}`;
      const zipFileName = (id) => `${fileName(id)}.zip`;

      let targetPopulationName = "PaymentPlanTargetPopulation";
      let paymentPlanUnicefId;
      let fspXlsxFilenames;

      //New Payment Plan page
      paymentModule.createPaymentPlan(targetPopulationName);

      cy.wait(3000); // eslint-disable-line cypress/no-unnecessary-waiting

      return; // TODO: make this work

      //Payment Plan Details page
      cy.get('[data-cy="page-header-container"]').contains("Payment Plan ID", {
        timeout: 10000,
      });
      cy.get('[data-cy="pp-unicef-id"]')
        .then(($el) => {
          paymentPlanUnicefId = $el.text();
        })
        .then(() => {
          cy.get("h6").contains("Details");
          cy.get("h6").contains("Results");
          cy.get("h6").contains("Payee List");
          cy.get("h6").contains("Activity Log");

          //Lock plan
          cy.get('[data-cy="button-lock-plan"]').click({
            force: true,
          });
          cy.get('[data-cy="button-submit"]').click({
            force: true,
          });

          //Entitlements
          cy.get("[data-cy=input-entitlement-formula]").should("exist");
          cy.get("[data-cy=input-entitlement-formula] > .MuiSelect-root").click(
            {
              force: true,
            }
          );
          cy.get('[data-cy="input-entitlement-formula"]').click({
            force: true,
          });
          cy.uniqueSeed().then((seed) => {
            cy.get("li").contains(`Rule-${seed}`).click({ force: true });
          });
          cy.get('[data-cy="button-apply-steficon"]').click({ force: true });
          cy.reload();
          cy.get('[data-cy="total-entitled-quantity-usd"]').contains("USD");
          // TODO: check the amount

          //Set up FSP
          cy.get('[data-cy="button-set-up-fsp"]').click({ force: true });
          cy.get('[data-cy="page-header-container"]').contains("Set up FSP", {
            timeout: 10000,
          });
          cy.get(
            '[data-cy="select-deliveryMechanisms[0].deliveryMechanism"]'
          ).click();
          cy.get('[data-cy="select-option-Transfer"]').click();
          cy.get('[data-cy="button-next-save"]').click({ force: true });
          cy.get('[data-cy="select-deliveryMechanisms[0].fsp"]');
          cy.get('[data-cy="select-deliveryMechanisms[0].fsp"]').click();
          cy.get('[data-cy="select-option-Test FSP Transfer"]').click();
          cy.get('[data-cy="button-next-save"]').click({ force: true });
          cy.contains("Volume by Delivery Mechanism");
          cy.get("[data-cy='button-lock-plan']").click({ force: true });
          cy.get("[data-cy='button-submit']").click({ force: true });
          cy.get("[data-cy='status-container']").contains("FSP LOCKED");

          //Acceptance Process
          cy.get("[data-cy='button-send-for-approval']").click({ force: true });
          cy.wait(1000);
          cy.reload(); // this shouldn't be needed but there's some bug here with which reload helps
          cy.contains("Acceptance Process");
          cy.get("[data-cy='button-approve']").click({ force: true });
          cy.get("[data-cy='button-submit']").click({ force: true });
          cy.get('[data-cy=""]').contains("IN AUTHORIZATION");
          cy.get("[data-cy='button-authorize']").click({ force: true });
          cy.get("[data-cy='button-submit']").click({ force: true });
          cy.get('[data-cy="status-container"]').contains("IN REVIEW");
          cy.get("[data-cy='button-mark-as-released']").click({ force: true });
          cy.get("[data-cy='button-submit']").click({ force: true });
          cy.get('[data-cy="status-container"]').contains("ACCEPTED");

          // //XLSX template - can be used in another spec
          // cy.get('[data-cy="button-export-xlsx"]').click({ force: true });
          // cy.wait(1000); // eslint-disable-line cypress/no-unnecessary-waiting
          // cy.reload();
          // cy.wait(1000); // eslint-disable-line cypress/no-unnecessary-waiting
          // const nameXlsx = xlsxFileName(paymentPlanUnicefId);
          // const downloadedFilePathXlsx = `${downloadsFolder}/${nameXlsx}`;
          // cy.exec(
          //   `node cypress/scripts/fillXlsxEntitlements.js ${downloadedFilePathXlsx}`
          //   );
          // cy.get('[data-cy="button-download-template"]').click({ force: true });
          // const nameTemplate = xlsxFileName(paymentPlanUnicefId);
          // const filledFilePathTemplate = `out_${nameTemplate}`;
          // cy.get('[data-cy="button-import"]').click({ force: true });
          // cy.fixture(filledFilePathTemplate, "base64").then((fileContent) => {
          //   cy.get('[data-cy="file-input"]').upload({
          //     fileContent,
          //     fileName: name,
          //     mimeType:
          //       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
          //     encoding: "base64",
          //   });
          // });
          // cy.get('[data-cy="button-import-entitlement"').click({ force: true });
          // cy.wait(2000); // eslint-disable-line cypress/no-unnecessary-waiting
          // cy.reload();
          // cy.get("td").should("not.contain", "Missing");

          cy.get('[data-cy="button-export-xlsx"]').click({ force: true });
          cy.wait(500); // eslint-disable-line cypress/no-unnecessary-waiting
          cy.reload();
          cy.get('[data-cy="button-download-xlsx"]').click({ force: true });
          cy.wait(500); // eslint-disable-line cypress/no-unnecessary-waiting
          const nameZip = zipFileName(paymentPlanUnicefId);
          const downloadedFilePathZip = `${downloadsFolder}/${nameZip}`;
          cy.exec(`unzip ${downloadedFilePathZip} -d ${downloadsFolder}`);
          const currentRunFileName = fileName(paymentPlanUnicefId);
          cy.exec(
            `find ${downloadsFolder} | grep ${currentRunFileName} | grep FSP | sed 's@.*/@@'`
          )
            .then((result) => {
              fspXlsxFilenames = result.stdout.split("\n");
              expect(fspXlsxFilenames.length).to.eq(1);
            })
            .then(() => {
              //Reconciliation Info
              const fspFilename = fspXlsxFilenames[0];
              const downloadedFilePath = `${downloadsFolder}/${fspFilename}`;
              cy.exec(
                `node cypress/scripts/fillXlsxReconciliation.js "${downloadedFilePath}"`
              );
              const filledFilePath = `out_${fspFilename}`;
              cy.log(filledFilePath);
              cy.get('[data-cy="button-import"]').click({ force: true });
              cy.fixture(filledFilePath, "base64").then((fileContent) => {
                cy.get('[data-cy="file-input"]').attachFile({
                  fileContent,
                  fileName: filledFilePath,
                  mimeType:
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                  encoding: "base64",
                });
              });
              cy.get('[data-cy="file-input"]').click({ force: true });
              // cy.get('[data-cy="imported-file-name"]').should('exist'); // TODO
              cy.get('[data-cy="button-import-submit"]').click({ force: true });
              cy.wait(1000);
              cy.get("p").should("not.contain", "Errors");
              cy.wait(500); // eslint-disable-line cypress/no-unnecessary-waiting
              cy.reload();
              cy.get('[data-cy="delivered-quantity-cell"]').each(($el) => {
                cy.wrap($el).should("contain", "AFN");
                cy.wrap($el).should("contain", "500");
              });
              cy.get('[data-cy="status-container"]').contains("FINISHED");
            });
        });
    });
    it("Select Entitlement Formula", () => {});
    it("Set up FSP", () => {});
    it("Create Exclude", () => {});
    it("Choose field from Payee List", () => {});
    it("Lock FSP", () => {});
    it("Unlock FSP", () => {});
    it("Send for approval", () => {});
    it("Approve", () => {});
    it("Reject from all points of process", () => {});
    it("Authorize", () => {});
    it("Export XLSX", () => {});
    it("Check Acceptance Process", () => {});
    context("Payment Filters", () => {
      it.skip("Payment Search filter", () => {});
      it.skip("Payment Status filter", () => {});
      it.skip("Payment Entitled Quantity filter", () => {});
      it.skip("Payment Dispersion Date filter", () => {});
    });
  });
  describe.skip("E2E tests Payment", () => {});

  describe("Regression tests Payment", () => {
    it("174517: Check clear cash", () => {
      cy.navigateToHomePage();
      paymentModule.getButtonPaymentModule().click();
      paymentModule.clearCache();
      paymentModule.getTitle().contains(paymentModule.textTitle);
    });
  });
});
