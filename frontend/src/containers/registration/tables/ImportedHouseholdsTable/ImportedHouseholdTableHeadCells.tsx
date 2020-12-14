import { HeadCell } from '../../../../components/table/EnhancedTableHead';
import { ImportedHouseholdMinimalFragment } from '../../../../__generated__/graphql';

export const headCells: HeadCell<ImportedHouseholdMinimalFragment>[] = [
  {
    disablePadding: false,
    label: '',
    id: '',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Source ID',
    id: 'id',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Head of Household',
    id: 'head_of_household__full_name',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Household Size',
    id: 'size',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Administrative Level 2',
    id: 'admin1',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Data Collected',
    id: 'firstRegistrationDate',
    numeric: false,
  },
];
