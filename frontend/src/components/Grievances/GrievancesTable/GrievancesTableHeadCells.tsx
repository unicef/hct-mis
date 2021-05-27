import {HeadCell} from '../../table/EnhancedTableHead';
import {AllGrievanceTicketQuery} from '../../../__generated__/graphql';

export const headCells: HeadCell<
  AllGrievanceTicketQuery['allGrievanceTicket']['edges'][number]['node']
>[] = [
  {
    disablePadding: false,
    label: 'Ticket Id',
    id: 'id',
    numeric: false,
    dataCy: 'ticket-id',
  },
  {
    disablePadding: false,
    label: 'Status',
    id: 'status',
    numeric: false,
    dataCy: 'status',
  },
  {
    disablePadding: false,
    label: 'Assigned to',
    id: 'assigned_to__last_name',
    numeric: false,
    dataCy: 'assignedTo',
  },
  {
    disablePadding: false,
    label: 'Category',
    id: 'category',
    numeric: false,
    dataCy: 'category',
  },
  {
    disablePadding: false,
    label: 'Household Id',
    id: 'household_unicef_id',
    numeric: false,
    dataCy: 'householdId',
  },
  {
    disablePadding: false,
    label: 'Creation date',
    id: 'created_at',
    numeric: false,
    dataCy: 'createdAt',
  },
  {
    disablePadding: false,
    label: 'Last modified date',
    id: 'user_modified',
    numeric: false,
    dataCy: 'userModified',
  },
];
