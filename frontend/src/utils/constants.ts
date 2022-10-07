import {
  PaymentPlanBackgroundActionStatus,
  PaymentPlanStatus,
  ProgramStatus,
  TargetPopulationStatus,
} from '../__generated__/graphql';

export const TARGETING_STATES = {
  NONE: 'None',
  [TargetPopulationStatus.Open]: 'Open',
  [TargetPopulationStatus.Locked]: 'Locked',
  [TargetPopulationStatus.ReadyForCashAssist]: 'Ready For Cash Assist',
  [TargetPopulationStatus.ReadyForPaymentModule]: 'Ready For Payment Module',
  [TargetPopulationStatus.Processing]: 'Processing',
  [TargetPopulationStatus.SteficonWait]: 'Steficon Wait',
  [TargetPopulationStatus.SteficonRun]: 'Steficon Run',
  [TargetPopulationStatus.SteficonCompleted]: 'Steficon Completed',
  [TargetPopulationStatus.SteficonError]: 'Steficon Error',
  [TargetPopulationStatus.Assigned]: 'Assigned',
};

export const PROGRAM_STATES = {
  [ProgramStatus.Active]: 'Active',
  [ProgramStatus.Draft]: 'Draft',
  [ProgramStatus.Finished]: 'Finished',
};

export const PAYMENT_PLAN_STATES = {
  [PaymentPlanStatus.Open]: 'Open',
  [PaymentPlanStatus.Locked]: 'Locked',
  [PaymentPlanStatus.LockedFsp]: 'FSP Locked',
  [PaymentPlanStatus.InApproval]: 'In Approval',
  [PaymentPlanStatus.InAuthorization]: 'In Authorization',
  [PaymentPlanStatus.InReview]: 'In Review',
  [PaymentPlanStatus.Accepted]: 'Accepted',
};

export const PAYMENT_PLAN_BACKGROUND_ACTION_STATES = {
  [PaymentPlanBackgroundActionStatus.SteficonRun]: 'Steficon Run',
  [PaymentPlanBackgroundActionStatus.SteficonError]: 'Steficon Error',
  [PaymentPlanBackgroundActionStatus.XlsxExporting]: 'XLSX Exporting',
  [PaymentPlanBackgroundActionStatus.XlsxExportError]: 'XLSX Export Error',
  [PaymentPlanBackgroundActionStatus.XlsxImportingEntitlements]:
    'XLSX Importing Entitlements',
  [PaymentPlanBackgroundActionStatus.XlsxImportingReconciliation]:
    'XLSX Importing Reconciliation',
  [PaymentPlanBackgroundActionStatus.XlsxImportError]: 'XLSX Import Error',
};

export const PAYMENT_PLAN_ACTIONS = {
  LOCK: 'LOCK',
  UNLOCK: 'UNLOCK',
  SEND_FOR_APPROVAL: 'SEND_FOR_APPROVAL',
  APPROVE: 'APPROVE',
  AUTHORIZE: 'AUTHORIZE',
  REVIEW: 'REVIEW',
  REJECT: 'REJECT',
};

export const GRIEVANCE_TICKET_STATES = {
  NEW: 1,
  ASSIGNED: 2,
  IN_PROGRESS: 3,
  ON_HOLD: 4,
  FOR_APPROVAL: 5,
  CLOSED: 6,
};

export const GRIEVANCE_CATEGORIES = {
  PAYMENT_VERIFICATION: '1',
  DATA_CHANGE: '2',
  SENSITIVE_GRIEVANCE: '3',
  GRIEVANCE_COMPLAINT: '4',
  NEGATIVE_FEEDBACK: '5',
  REFERRAL: '6',
  POSITIVE_FEEDBACK: '7',
  DEDUPLICATION: '8',
  SYSTEM_FLAGGING: '9',
};

export const GRIEVANCE_ISSUE_TYPES = {
  EDIT_HOUSEHOLD: '13',
  EDIT_INDIVIDUAL: '14',
  DELETE_INDIVIDUAL: '15',
  ADD_INDIVIDUAL: '16',
  DELETE_HOUSEHOLD: '17',
};

export const REPORT_TYPES = {
  INDIVIDUALS: '1',
  HOUSEHOLD_DEMOGRAPHICS: '2',
  CASH_PLAN_VERIFICATION: '3',
  PAYMENTS: '4',
  PAYMENT_VERIFICATION: '5',
  CASH_PLAN: '6',
  PROGRAM: '7',
  INDIVIDUALS_AND_PAYMENT: '8',
};

export const REPORTING_STATES = {
  PROCESSING: 1,
  GENERATED: 2,
  FAILED: 3,
};


export const COLLECT_TYPES_MAPPING = {
  "A_": "Unknown",
  "A_0": "None",
  "A_1": "Full",
  "A_2": "Partial",
}
