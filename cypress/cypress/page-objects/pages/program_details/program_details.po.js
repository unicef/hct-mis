import BaseComponent from "../../base.component";

export default class ProgramDetails extends BaseComponent {
  // Locators
  buttonActivateProgram = 'button[data-cy="button-activate-program"]';
  buttonRemoveProgram = 'button[data-cy="button-remove-program"]';
  buttonEditProgram = 'button[data-cy="button-edit-program"]';
  buttonCopyProgram = 'button[data-cy="button-copy-program"]';
  dialogPopupActivate = 'div[data-cy="dialog-actions-container"]';
  labelTotalNumberOfHouseholds =
    'div[data-cy="label-Total Number of Households"]';
  labelIndividualsData =
    'div[data-cy="label-Does this programme use individuals’ data for targeting or entitlement calculation?"]';
  labelCASH = 'div[data-cy="label-CASH+"]';
  labelDescription = 'div[data-cy="label-Description"]';
  labelAdministrativeAreasOfImplementation =
    'div[data-cy="label-Administrative Areas of implementation"]';
  labelFrequencyOfPayment = 'div[data-cy="label-Frequency of Payment"]';
  labelScope = 'div[data-cy="label-Scope"]';
  labelSector = 'div[data-cy="label-Sector"]';
  labelENDDATE = 'div[data-cy="label-END DATE"]';
  labelSTARTDATE = 'div[data-cy="label-START DATE"]';
  statusContainer = 'div[data-cy="status-container"]';
  labelStatus = 'div[data-cy="label-status"]';
  pageHeaderTitle = 'h5[data-cy="page-header-title"]';

  tablePagination = 'div[data-cy="table-pagination"]';
  cashPlanTableRow = 'tr[data-cy="cash-plan-table-row"]';
  tableLabel = 'span[data-cy="table-label"]';
  tableTitle = 'h6[data-cy="table-title"]';
  buttonAddNewProgramCycle = 'button[data-cy="button-add-new-program-cycle"]';
  buttonDataCyButtonEditProgramCycle =
    'button[data-cy="button-edit-program-cycle"]';
  buttonCreate = 'button[data-cy="button-create"]';
  buttonCancel = 'button[data-cy="button-cancel"]';
  inputDataCyDateInputNewProgramCycleEndDate =
    'input[data-cy="date-input-newProgramCycleEndDate"]';
  inputDataCyDateInputNewProgramCycleStartDate =
    'input[data-cy="date-input-newProgramCycleStartDate"]';
  inputDataCyInputNewProgramCycleName =
    'input[data-cy="input-newProgramCycleName"]';

  // Texts
  textTableTitle = "Programme Cycles";
  textProgrammeCycleID = "Programme Cycle ID";
  text = "Programme Cycle Title";
  text = "Status";
  text = "Total Entitled Quantity";
  text = "Total Undelivered Quantity";
  text = "Total Delivered Quantity";
  text = "Start Date";
  text = "End Date";
  getButtonActivateProgram = () => cy.get(this.buttonActivateProgram);
  getButtonRemoveProgram = () => cy.get(this.buttonRemoveProgram);
  getButtonEditProgram = () => cy.get(this.buttonEditProgram);
  getButtonCopyProgram = () => cy.get(this.buttonCopyProgram);
  getDialogPopupActivate = () => cy.get(this.dialogPopupActivate);
  getLabelTotalNumberOfHouseholds = () =>
    cy.get(this.labelTotalNumberOfHouseholds);
  getLabelIndividualsData = () => cy.get(this.labelIndividualsData);
  getLabelCASH = () => cy.get(this.labelCASH);
  getLabelDescription = () => cy.get(this.labelDescription);
  getLabelAdministrativeAreasOfImplementation = () =>
    cy.get(this.labelAdministrativeAreasOfImplementation);
  getLabelFrequencyOfPayment = () => cy.get(this.labelFrequencyOfPayment);
  getLabelScope = () => cy.get(this.labelScope);
  getLabelSector = () => cy.get(this.labelSector);
  getLabelENDDATE = () => cy.get(this.labelENDDATE);
  getLabelSTARTDATE = () => cy.get(this.labelSTARTDATE);
  getStatusContainer = () => cy.get(this.statusContainer);
  getLabelStatus = () => cy.get(this.labelStatus);
  getPageHeaderTitle = () => cy.get(this.pageHeaderTitle);
  getTablePagination = () => cy.get(this.tablePagination);
  getTashPlanTableRow = () => cy.get(this.cashPlanTableRow);
  getTableLabel = () => cy.get(this.tableLabel);
  getTableTitle = () => cy.get(this.tableTitle);
}
