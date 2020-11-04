import { HeadCell } from '../../../components/table/EnhancedTableHead';
import { TargetPopulationNode } from '../../../__generated__/graphql';

export const headCells: HeadCell<TargetPopulationNode>[] = [
  {
    disablePadding: false,
    label: 'Id',
    id: 'id',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Head of Household',
    id: 'headOfHousehold',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Household size',
    id: 'householdSize',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Administrative Level 2',
    id: 'location',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Last Inspection',
    id: 'lastEditedAt',
    numeric: false,
  },
];
