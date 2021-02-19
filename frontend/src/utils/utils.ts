import moment from 'moment';
import { GraphQLError } from 'graphql';
import { theme as themeObj } from '../theme';
import {
  AllProgramsQuery,
  ChoiceObject,
  ProgramStatus,
} from '../__generated__/graphql';
import { ValidationGraphQLError } from '../apollo/client';
import { GRIEVANCE_CATEGORIES, TARGETING_STATES } from './constants';

const Gender = new Map([
  ['MALE', 'Male'],
  ['FEMALE', 'Female'],
]);

const IdentificationType = new Map([
  ['NA', 'N/A'],
  ['BIRTH_CERTIFICATE', 'Birth Certificate'],
  ['DRIVING_LICENSE', 'Driving License'],
  ['UNHCR_ID_CARD', 'UNHCR ID Card'],
  ['NATIONAL_ID', 'National ID'],
  ['NATIONAL_PASSPORT', 'National Passport'],
]);

export const getIdentificationType = (idType: string): string => {
  if (IdentificationType.has(idType)) {
    return IdentificationType.get(idType);
  }
  return idType;
};
export const sexToCapitalize = (sex: string): string => {
  if (Gender.has(sex)) {
    return Gender.get(sex);
  }
  return sex;
};

export function opacityToHex(opacity: number): string {
  return Math.floor(opacity * 0xff).toString(16);
}

export function programStatusToColor(
  theme: typeof themeObj,
  status: string,
): string {
  switch (status) {
    case 'DRAFT':
      return theme.hctPalette.gray;
    case 'ACTIVE':
      return theme.hctPalette.green;
    case 'FINISHED':
      return theme.hctPalette.gray;
    default:
      return theme.hctPalette.oragne;
  }
}
export function maritalStatusToColor(
  theme: typeof themeObj,
  status: string,
): string {
  switch (status) {
    case 'SINGLE':
      return theme.hctPalette.green;
    case 'MARRIED':
      return theme.hctPalette.oragne;
    case 'WIDOW':
      return theme.hctPalette.gray;
    case 'DIVORCED':
      return theme.hctPalette.gray;
    case 'SEPARATED':
      return theme.hctPalette.gray;
    default:
      return theme.hctPalette.gray;
  }
}
export function populationStatusToColor(
  theme: typeof themeObj,
  status: string,
): string {
  switch (status) {
    case 'ACTIVE':
      return theme.hctPalette.green;
    default:
      return theme.hctPalette.gray;
  }
}

export function cashPlanStatusToColor(
  theme: typeof themeObj,
  status: string,
): string {
  switch (status) {
    case 'STARTED':
      return theme.hctPalette.green;
    case 'COMPLETE':
      return theme.hctPalette.gray;
    default:
      return theme.hctPalette.oragne;
  }
}
export function paymentRecordStatusToColor(
  theme: typeof themeObj,
  status: string,
): string {
  switch (status) {
    case 'SUCCESS':
      return theme.hctPalette.green;
    case 'PENDING':
      return theme.hctPalette.oragne;
    default:
      return theme.palette.error.main;
  }
}
export function paymentVerificationStatusToColor(
  theme: typeof themeObj,
  status: string,
): string {
  switch (status) {
    case 'ACTIVE':
      return theme.hctPalette.green;
    case 'PENDING':
      return theme.hctPalette.oragne;
    case 'FINISHED':
      return theme.hctPalette.gray;
    default:
      return theme.palette.error.main;
  }
}

export function verificationRecordsStatusToColor(
  theme: typeof themeObj,
  status: string,
): string {
  switch (status) {
    case 'PENDING':
      return theme.hctPalette.gray;
    case 'RECEIVED':
      return theme.hctPalette.green;
    case 'NOT_RECEIVED':
      return theme.palette.error.main;
    case 'RECEIVED_WITH_ISSUES':
      return theme.hctPalette.oragne;
    default:
      return theme.palette.error.main;
  }
}
export function registrationDataImportStatusToColor(
  theme: typeof themeObj,
  status: string,
): string {
  switch (status) {
    case 'APPROVED':
      return theme.hctPalette.green;
    case 'MERGED':
      return theme.hctPalette.gray;
    case 'IN_PROGRESS':
      return theme.hctPalette.oragne;
    default:
      return theme.hctPalette.oragne;
  }
}

export function targetPopulationStatusToColor(
  theme: typeof themeObj,
  status: string,
): string {
  switch (status) {
    case 'DRAFT':
      return theme.hctPalette.gray;
    case 'APPROVED':
      return theme.hctPalette.oragne;
    case 'FINALIZED':
      return theme.hctPalette.green;
    default:
      return theme.palette.error.main;
  }
}

export function userStatusToColor(
  theme: typeof themeObj,
  status: string,
): string {
  switch (status) {
    case 'INVITED':
      return theme.hctPalette.gray;
    case 'ACTIVE':
      return theme.hctPalette.green;
    case 'INACTIVE':
      return theme.palette.error.main;
    default:
      return theme.palette.error.main;
  }
}
export function grievanceTicketStatusToColor(
  theme: typeof themeObj,
  status: string,
): string {
  switch (status) {
    case 'New':
      return theme.hctPalette.oragne;
    case 'Assigned':
      return theme.hctPalette.darkerBlue;
    case 'In Progress':
      return theme.hctPalette.green;
    case 'On Hold':
      return theme.palette.error.main;
    case 'For Approval':
      return theme.hctPalette.darkBrown;
    case 'Closed':
      return theme.hctPalette.gray;
    default:
      return theme.palette.error.main;
  }
}

export function reportStatusToColor(
  theme: typeof themeObj,
  status: string,
): string {
  switch (status) {
    case 'Generated':
      return theme.hctPalette.green;
    case 'Processing':
      return theme.hctPalette.gray;
    default:
      return theme.palette.error.main;
  }
}

export function selectFields(
  fullObject,
  keys: string[],
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
): { [key: string]: any } {
  return keys.reduce((acc, current) => {
    acc[current] = fullObject[current];
    return acc;
  }, {});
}

export function camelToUnderscore(key): string {
  return key.replace(/([A-Z])/g, '_$1').toLowerCase();
}

export function columnToOrderBy(
  column: string,
  orderDirection: string,
): string {
  if (column.startsWith('-')) {
    const clearColumn = column.replace('-', '');
    return camelToUnderscore(
      `${orderDirection === 'asc' ? '-' : ''}${clearColumn}`,
    );
  }
  return camelToUnderscore(`${orderDirection === 'desc' ? '-' : ''}${column}`);
}

export function choicesToDict(
  choices: ChoiceObject[],
): { [key: string]: string } {
  return choices.reduce((previousValue, currentValue) => {
    const newDict = { ...previousValue };
    newDict[currentValue.value] = currentValue.name;
    return newDict;
  }, {});
}

export function programStatusToPriority(status: ProgramStatus): number {
  switch (status) {
    case ProgramStatus.Draft:
      return 1;
    case ProgramStatus.Active:
      return 2;
    default:
      return 3;
  }
}
export function decodeIdString(idString): string | null {
  if (!idString) {
    return null;
  }
  const decoded = atob(idString);
  return decoded.split(':')[1];
}

export function programCompare(
  a: AllProgramsQuery['allPrograms']['edges'][number],
  b: AllProgramsQuery['allPrograms']['edges'][number],
): number {
  const statusA = programStatusToPriority(a.node.status);
  const statusB = programStatusToPriority(b.node.status);
  return statusA > statusB ? 1 : -1;
}

export function formatCurrency(amount: number): string {
  const amountCleared = amount || 0;
  return `${amountCleared.toLocaleString('en-US', {
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })} USD`;
}

export function formatCurrencyWithSymbol(
  amount: number,
  currency = 'USD',
): string {
  const amountCleared = amount || 0;
  return new Intl.NumberFormat('en-US', { style: 'currency', currency }).format(
    amountCleared,
  );
}

export function getPercentage(
  partialValue: number,
  totalValue: number,
): string {
  if (!totalValue) {
    return '0%';
  }
  return `${((partialValue / totalValue) * 100).toFixed(2)}%`;
}

export function formatNumber(value: number): string {
  if (!value && value !== 0) return '';
  return value.toLocaleString(undefined, { maximumFractionDigits: 0 });
}

export function getAgeFromDob(date: string): number {
  return moment().diff(moment(date), 'years');
}

export function targetPopulationStatusMapping(status): string {
  return TARGETING_STATES[status];
}

// eslint-disable-next-line @typescript-eslint/explicit-function-return-type
export function stableSort(array, comparator) {
  const stabilizedThis = array.map((el, index) => [el, index]);
  stabilizedThis.sort((a, b) => {
    const order = comparator(a[0], b[0]);
    if (order !== 0) return order;
    return a[1] - b[1];
  });
  return stabilizedThis.map((el) => el[0]);
}

export function descendingComparator(a, b, orderBy): number {
  if (b[orderBy] < a[orderBy]) {
    return -1;
  }
  if (b[orderBy] > a[orderBy]) {
    return 1;
  }
  return 0;
}

export function getComparator(
  order,
  orderBy,
): (a: number, b: number) => number {
  return order === 'desc'
    ? (a, b) => descendingComparator(a, b, orderBy)
    : (a, b) => -descendingComparator(a, b, orderBy);
}

export function reduceChoices(choices): { [id: number]: string } {
  return choices.reduce((previousValue, currentValue) => {
    // eslint-disable-next-line no-param-reassign
    previousValue[currentValue.value] = currentValue.name;
    return previousValue;
  }, {});
}

export function renderUserName(user): string {
  if (!user) {
    return '-';
  }
  return user?.firstName
    ? `${user?.firstName} ${user?.lastName}`
    : `${user?.email}`;
}

const grievanceTypeIssueTypeDict: { [id: string]: boolean | string } = {
  [GRIEVANCE_CATEGORIES.NEGATIVE_FEEDBACK]: false,
  [GRIEVANCE_CATEGORIES.POSITIVE_FEEDBACK]: false,
  [GRIEVANCE_CATEGORIES.REFERRAL]: false,
  [GRIEVANCE_CATEGORIES.GRIEVANCE_COMPLAINT]: false,
  [GRIEVANCE_CATEGORIES.SENSITIVE_GRIEVANCE]: true,
  [GRIEVANCE_CATEGORIES.DATA_CHANGE]: true,
};

// eslint-disable-next-line @typescript-eslint/explicit-function-return-type
export function thingForSpecificGrievanceType(
  ticket: { category: number | string; issueType?: number | string },
  thingDict,
  defaultThing = null,
  categoryWithIssueTypeDict = grievanceTypeIssueTypeDict,
) {
  const category = ticket.category?.toString();
  const issueType = ticket.issueType?.toString();
  if (!(category in thingDict)) {
    return defaultThing;
  }
  const categoryThing = thingDict[category];
  if (
    categoryWithIssueTypeDict[category] === 'IGNORE' ||
    (!categoryWithIssueTypeDict[category] &&
      (issueType === null || issueType === undefined))
  ) {
    return categoryThing;
  }
  if (!(issueType in categoryThing)) {
    return defaultThing;
  }
  return categoryThing[issueType];
}

export const isInvalid = (fieldname: string, errors, touched): boolean =>
  errors[fieldname] && touched[fieldname];

export const anon = (inputStr: string, shouldAnonymize: boolean): string => {
  if (!inputStr) return null;
  return shouldAnonymize
    ? inputStr
        .split(' ')
        .map((el) => el.substring(0, 2) + '*'.repeat(3))
        .join(' ')
    : inputStr;
};

export const isPermissionDeniedError = (error): boolean =>
  error?.message.includes('Permission Denied');

// eslint-disable-next-line @typescript-eslint/explicit-function-return-type
export const getFullNodeFromEdgesById = (edges, id) => {
  if (!edges) return null;
  return edges.find((edge) => edge.node.id === id)?.node || null;
};

export const getFlexFieldTextValue = (key, value, fieldAttribute): string => {
  let textValue = value;
  if (fieldAttribute.type === 'SELECT_ONE') {
    textValue = fieldAttribute.choices.find((item) => item.value === value)
      .labelEn;
  }
  if (fieldAttribute.type === 'SELECT_MANY') {
    const values = fieldAttribute.choices.filter((item) =>
      value.includes(item.value),
    );
    textValue = values.map((item) => item.labelEn).join(', ');
  }
  return textValue;
};

export const handleValidationErrors = (
  fieldName,
  e,
  setFieldError,
  showMessage,
): { nonValidationErrors: GraphQLError[] } => {
  const validationErrors = e.graphQLErrors.filter(
    (error) => error instanceof ValidationGraphQLError,
  );
  const nonValidationErrors = e.graphQLErrors.filter(
    (error) => !(error instanceof ValidationGraphQLError),
  );
  for (const validationError of validationErrors) {
    Object.entries(validationError.validationErrors[fieldName]).map(
      // eslint-disable-next-line array-callback-return
      (entry) => {
        if (entry[0] === '__all__') {
          showMessage((entry[1] as string[]).join('\n'));
        }
        setFieldError(entry[0], (entry[1] as string[]).join('\n'));
      },
    );
  }
  return { nonValidationErrors };
};
