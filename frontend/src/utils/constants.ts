import {
  PaymentPlanStatus,
  TargetPopulationStatus,
} from '../__generated__/graphql';

export const TARGETING_STATES = {
  NONE: 'None',
  [TargetPopulationStatus.Draft]: 'Open',
  [TargetPopulationStatus.Locked]: 'Locked',
  [TargetPopulationStatus.ReadyForCashAssist]: 'Ready For Cash Assist',
  [TargetPopulationStatus.Ready]: 'Ready',
  [TargetPopulationStatus.Processing]: 'Processing',
  [TargetPopulationStatus.SteficonWait]: 'Steficon Wait',
  [TargetPopulationStatus.SteficonRun]: 'Steficon Run',
  [TargetPopulationStatus.SteficonCompleted]: 'Steficon Completed',
  [TargetPopulationStatus.SteficonError]: 'Steficon Error',
  [TargetPopulationStatus.Assigned]: 'Assigned',
};

export const PAYMENT_PLAN_STATES = {
  [PaymentPlanStatus.Open]: 'Open',
  [PaymentPlanStatus.Locked]: 'Locked',
  [PaymentPlanStatus.InApproval]: 'In Approval',
  [PaymentPlanStatus.InAuthorization]: 'In Authorization',
  [PaymentPlanStatus.InReview]: 'In Review',
  [PaymentPlanStatus.Accepted]: 'Accepted',
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
