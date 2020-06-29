import { HeadCell } from '../../../components/table/EnhancedTableHead';
import { TargetPopulationNode } from '../../../__generated__/graphql';

export const headCells: HeadCell<TargetPopulationNode>[] = [
    {
      disablePadding: false,
      label: 'Cash Plan ID',
      id: 'id',
      numeric: false,
    },
    {
      disablePadding: false,
      label: 'Verification Status',
      id: 'verificationStatus',
      numeric: false,
    },
    {
      disablePadding: false,
      label: 'FSP',
      id: 'fsp',
      numeric: false,
    },
    {
      disablePadding: false,
      label: 'Modality',
      id: 'modality',
      numeric: false,
    },
    {
      disablePadding: false,
      label: 'Cash Amount',
      id: 'cashAmount',
      numeric: true,
    },
    {
      disablePadding: false,
      label: 'Timeframe',
      id: 'timeframe',
      numeric: false,
    },
    {
      disablePadding: false,
      label: 'Programme',
      id: 'programme',
      numeric: false,
    },
  ];
