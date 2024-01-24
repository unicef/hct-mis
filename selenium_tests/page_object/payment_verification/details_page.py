from page_object.base_components import BaseComponents


class PVDetailsPage extends BaseComponent {
  // Locators
  paymentVerificationTitle = 'h5[data-cy="page-header-title"]';
  createVerificationPlan = 'button[data-cy="button-new-plan"]';
  divPaymentDetails = 'div[data-cy="div-payment-plan-details"]';
  gridPaymentDetails = 'div[data-cy="grid-payment-plan-details"]';
  divBankReconciliation = 'div[data-cy="grid-bank-reconciliation"]';
  divVerificationPlansSummary =
    'div[data-cy="grid-verification-plans-summary"]';
  tableTitle = 'h6[data-cy="table-label"]';
  gridBankReconciliation = 'div[data-cy="grid-bank-reconciliation"]';
  summaryStatus = 'div[data-cy="verification-plans-summary-status"]';
  statusVP = 'div[data-cy="verification-plan-status"]';
  summaryActivationDate =
    'div[data-cy="labelized-field-container-summary-activation-date"]';
  summaryCompletionDate =
    'div[data-cy="labelized-field-container-summary-completion-date"]';
  summaryNumberOfPlans =
    'div[data-cy="labelized-field-container-summary-number-of-plans"]';
  deletePlan = 'button[data-cy="button-delete-plan"]';
  deletePopUP = 'div[data-cy="dialog-actions-container"]';
  activatePlan = 'button[data-cy="button-activate-plan"]';
  discardPlan = 'button[data-cy="button-discard-plan"]';
  finishPlan = 'button[data-cy="button-ed-plan"]';
  editVP = 'button[data-cy="button-new-plan"]';
  // Create Verification Plan
  cvp = 'div[data-cy="dialog-title"]';
  cvpTabList = 'div[data-cy="tabs"]';
  cvpTab = 'button[role="tab"]';
  cvpTitle = 'div[data-cy="dialog-title"]';
  cvpSliderConfidenceInterval = 'span[data-cy="slider-confidence-interval"]';
  cvpInputAdminCheckbox = 'span[data-cy="input-adminCheckbox"]';
  cvpSubmit = 'button[data-cy="button-submit"]';
  labelVERIFICATIONCHANNEL = 'div[data-cy="label-VERIFICATION CHANNEL"]';

  // Texts
  textTitle = "Payment Verification";
  textPaymentPlanDetails = "Payment Plan Details";
  textCreateVerificationPlan = "CREATE VERIFICATION PLAN";
  textProgrammeName = "PROGRAMME NAME";
  textProgrammeID = "PROGRAMME ID";
  textPaymentRecords = "PAYMENT RECORDS";
  textStartDate = "START DATE";
  textEndDate = "END DATE";
  textBankReconciliation = "Bank reconciliation";
  textSuccessful = "SUCCESSFUL";
  textErroneus = "ERRONEOUS";
  textVerificationPlansSummary = "Verification Plans Summary";
  textSummaryStatus = "Status";
  textSummaryActivationDate = "Activation Date";
  textSummaryCompletionDate = "Completion Date";
  textSummaryNumberOfPlans = "Number of Verification Plans";
  textCVPTitle = "Create Verification Plan";
  textCVPConfidenceInterval = "Confidence Interval";

  // Elements
  getPaymentVerificationTitle = () => cy.get(this.paymentVerificationTitle);
  getCreateVerificationPlan = () => cy.get(this.createVerificationPlan);
  getPaymentPlanDetails = () => cy.get(this.divPaymentDetails);
  getProgrammeName = () =>
    this.getPaymentPlanDetails().get(this.gridPaymentDetails);
  getProgrammeID = () =>
    this.getPaymentPlanDetails().get(this.gridPaymentDetails);
  getPaymentRecords = () =>
    this.getPaymentPlanDetails().get(this.gridPaymentDetails);
  getStartDate = () =>
    this.getPaymentPlanDetails().get(this.gridPaymentDetails);
  getEndDate = () => this.getPaymentPlanDetails().get(this.gridPaymentDetails);
  getBankReconciliationTitle = () =>
    cy.get(this.divBankReconciliation).get(this.tableTitle);
  getSuccessful = () =>
    cy
      .get(this.divBankReconciliation)
      .eq(0)
      .get(this.gridBankReconciliation)
      .get("div")
      .eq(0);
  getErroneus = () =>
    cy
      .get(this.divBankReconciliation)
      .eq(0)
      .get(this.gridBankReconciliation)
      .get("div")
      .eq(1);
  getVerificationPlansSummary = () =>
    cy.get(this.divVerificationPlansSummary).get(this.tableTitle);
  getStatus = () => cy.get(this.summaryStatus);
  getActivationDate = () => cy.get(this.summaryActivationDate);
  getCompletionDate = () => cy.get(this.summaryCompletionDate);
  getNumberOfPlans = () => cy.get(this.summaryNumberOfPlans);
  getDeletePlan = () => cy.get(this.deletePlan);
  getDelete = () => cy.get(this.deletePopUP).get(this.cvpSubmit);
  getActivatePlan = () => cy.get(this.activatePlan);
  getActivate = () => cy.get(this.cvpSubmit);
  getDiscardPlan = () => cy.get(this.discardPlan);
  getDiscard = () => cy.get(this.cvpSubmit);
  getStatusVP = () => cy.get(this.statusVP);
  getFinishPlan = () => cy.get(this.finishPlan);
  getFinish = () => cy.get(this.cvpSubmit);
  getEditVP = () => cy.get(this.editVP);
  getMANUAL = () => cy.get("span").filter("MANUAL").eq(1);
  getXLSX = () => cy.get('input[value="XLSX"]').eq(1);
  getLabelVERIFICATIONCHANNEL = () => cy.get(this.labelVERIFICATIONCHANNEL);
  // Create Verification Plan
  getCVPTitle = () => cy.get(this.cvp).get(this.cvpTitle);
  getFullList = () => cy.get(this.cvp).get(this.cvpTab).eq(0);
  getRandomSampling = () => cy.get(this.cvp).get(this.cvpTab).eq(1);
  getCVPConfidenceInterval = () =>
    cy.get(this.cvp).get(this.cvpSliderConfidenceInterval);
  getCVPSave = () => cy.get(this.cvpSubmit);
  getCvpInputAdminCheckbox = () => cy.get(this.cvpInputAdminCheckbox);

  checkPaymentVerificationTitle() {
    this.getPaymentVerificationTitle().should("be.visible");
    this.getCreateVerificationPlan()
      .get("span")
      .contains(this.textCreateVerificationPlan);
  }

  checkGridPaymentDetails() {
    this.getProgrammeName().get("span").contains(this.textProgrammeName);
    this.getProgrammeID().get("span").contains(this.textProgrammeName);
    this.getPaymentRecords().get("span").contains(this.textProgrammeName);
    this.getStartDate().get("span").contains(this.textProgrammeName);
    this.getEndDate().get("span").contains(this.textProgrammeName);
  }

  checkBankReconciliationTitle() {
    this.getBankReconciliationTitle().contains(this.textBankReconciliation);
  }

  checkGridBankReconciliation() {
    this.getSuccessful().contains(this.textSuccessful);
    this.getErroneus().contains(this.textErroneus);
  }

  checkVerificationPlansSummaryTitle() {
    this.getVerificationPlansSummary().contains(
      this.textVerificationPlansSummary
    );
  }

  checkGridVerificationPlansSummary() {
    this.getStatus().get("span").contains(this.textSummaryStatus);
    this.getActivationDate().contains(this.textSummaryActivationDate);
    this.getCompletionDate().contains(this.textSummaryCompletionDate);
    this.getNumberOfPlans().contains(this.textSummaryNumberOfPlans);
  }

  checkCVPTitle() {
    this.getCVPTitle().contains(this.textCVPTitle);
  }

  checkVerificationPlan() {
    this.checkVerificationPlansSummaryTitle();
  }

  deleteVerificationPlan(num = 0) {
    this.getDeletePlan().scrollIntoView().should("be.visible");
    this.getDeletePlan().click();
    this.getDelete().should("be.visible");
    this.getDelete().click();
    this.getDelete().should("not.exist");
    this.getActivationDate().find("div").contains("-");
    this.getNumberOfPlans().contains(num);
  }

  discardVerificationPlan(num = 0) {
    this.getDiscardPlan().eq(num).scrollIntoView().click();
    this.getDiscard().scrollIntoView().click();
    this.getDiscard().should("not.exist");
    this.getDiscardPlan().should("not.exist");
    this.getDeletePlan().scrollIntoView();
  }

  checkPaymentPlanDetailsTitle() {
    this.getPaymentPlanDetails()
      .find("h6")
      .contains(this.textPaymentPlanDetails);
  }
  createNewVerificationPlan(num = 0) {
    this.checkPaymentVerificationTitle();
    this.getNumberOfPlans().then(($el) => {
      if ($el.find("div").text() === num.toString()) {
        this.getCreateVerificationPlan().click();
        this.checkCVPTitle();
        this.getRandomSampling().click();
        this.getCVPConfidenceInterval().should("be.visible");
        this.getCVPSave().click();
        this.checkVerificationPlan();
      }
    });
  }
}
