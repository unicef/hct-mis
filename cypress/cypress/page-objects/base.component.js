export default class BaseComponent {
  // Menu Locators
  navRegistrationDataImport = 'a[data-cy="nav-Registration Data Import"]';
  navProgrammePopulation = 'div[data-cy="nav-Programme Population"]';
  navHouseholds = 'a[data-cy="nav-Households"]';
  navIndividuals = 'a[data-cy="nav-Individuals"]';
  navProgrammeManagement = 'a[data-cy="nav-Programme Management"]';
  navProgrammeDetails = 'a[data-cy="nav-Programme Details"]';
  navTargeting = 'a[data-cy="nav-Targeting"]';
  navCashAssist = 'a[data-cy="nav-Cash Assist"]';
  navPaymentModule = 'a[data-cy="nav-Payment Module"]';
  navPaymentVerification = 'a[data-cy="nav-Payment Verification"]';
  navGrievance = 'div[data-cy="nav-Grievance"]';
  navGrievanceTickets = 'a[data-cy="nav-Grievance Tickets"]';
  navGrievanceDashboard = 'a[data-cy="nav-Grievance Dashboard"]';
  navFeedback = 'a[data-cy="nav-Feedback"]';
  navReporting = 'a[data-cy="nav-Reporting"]';
  navProgrammeUsers = 'a[data-cy="nav-Programme Users"]';
  navActivityLog = 'a[data-cy="nav-Activity Log"]';
  navResourcesKnowledgeBase = 'a[data-cy="nav-resources-Knowledge Base"]';
  navResourcesConversations = 'a[data-cy="nav-resources-Conversations"]';
  navResourcesToolsAndMaterials =
    'a[data-cy="nav-resources-Tools and Materials"]';
  navResourcesReleaseNote = 'a[data-cy="nav-resources-Release Note"]';
  headerTitle = 'h5[data-cy="page-header-title"]';
  globalProgramFilter = 'div[data-cy="global-program-filter"]';

  // Texts
  buttonPaymentVerificationText = "Payment Verification";
  buttonTargetingText = "Targeting";
  buttonGrievanceText = "Grievance";
  buttonGrievanceTicketsText = "Grievance Tickets";
  buttonGrievanceDashboardText = "Grievance Dashboard";
  buttonFeedbackText = "Feedback";

  // Elements)
  getMenuButtonRegistrationDataImport = () =>
    cy.get(this.navRegistrationDataImport);
  getMenuButtonProgrammePopulation = () => cy.get(this.navProgrammePopulation);
  getMenuButtonHouseholds = () => cy.get(this.navHouseholds);
  getMenuButtonIndividuals = () => cy.get(this.navIndividuals);
  getMenuButtonProgrammeManagement = () => cy.get(this.navProgrammeManagement);
  getMenuButtonProgrammeDetails = () => cy.get(this.navProgrammeDetails);
  getMenuButtonCashAssist = () => cy.get(this.navCashAssist);
  getMenuButtonPaymentModule = () => cy.get(this.navPaymentModule);
  getMenuButtonReporting = () => cy.get(this.navReporting);
  getMenuButtonProgrammeUsers = () => cy.get(this.navProgrammeUsers);
  getMenuButtonActivityLog = () => cy.get(this.navActivityLog);
  getMenuButtonResourcesKnowledgeBase = () =>
    cy.get(this.navResourcesKnowledgeBase);
  getMenuButtonResourcesConversations = () =>
    cy.get(this.navResourcesConversations);
  getMenuButtonResourcesToolsAndMaterials = () =>
    cy.get(this.navResourcesToolsAndMaterials);
  getMenuButtonResourcesReleaseNote = () =>
    cy.get(this.navResourcesReleaseNote);
  getMenuButtonPaymentVerification = () => cy.get(this.navPaymentVerification);
  getMenuButtonTargeting = () => cy.get(this.navTargeting);
  getMenuButtonGrievance = () => cy.get(this.navGrievance);
  getMenuButtonGrievanceTickets = () => cy.get(this.navGrievanceTickets);
  getMenuButtonGrievanceDashboard = () => cy.get(this.navGrievanceDashboard);
  getGlobalProgramFilter = () => cy.get(this.globalProgramFilter);
  getMenuButtonFeedback = () => cy.get(this.navFeedback);
  getHeaderTitle = () => cy.get(this.headerTitle);

  checkGrievanceMenu() {
    this.getMenuButtonGrievanceTickets().should("be.visible");
    this.getMenuButtonGrievanceDashboard().should("be.visible");
    this.getMenuButtonFeedback().should("be.visible");
  }
  clickMenuButtonPaymentVerification() {
    this.getMenuButtonPaymentVerification()
      .contains(this.buttonPaymentVerificationText)
      .click();
  }

  clickMenuButtonGrievance() {
    this.getMenuButtonGrievance().contains(this.buttonGrievanceText).click();
  }

  clickMenuButtonGrievanceTickets() {
    this.getMenuButtonGrievanceTickets()
      .contains(this.buttonGrievanceTicketsText)
      .click();
  }

  clickMenuButtonGrievanceDashboard() {
    this.getMenuButtonGrievanceDashboard()
      .contains(this.buttonGrievanceDashboardText)
      .click();
  }

  clickMenuButtonFeedback() {
    this.getMenuButtonFeedback().contains(this.buttonFeedbackText).click();
  }

  clickMenuButtonTargeting() {
    this.getMenuButtonTargeting().contains(this.buttonTargetingText).click();
  }

  pressEscapeFromElement(element) {
    element.focused().then(($el) => {
      if ($el.length) {
        element.type("{esc}");
      }
    });
  }
}
