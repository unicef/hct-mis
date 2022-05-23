import { IconButton, Box } from '@material-ui/core';
import TableCell from '@material-ui/core/TableCell';
import { Edit, Delete } from '@material-ui/icons';
import React from 'react';
import { useHistory } from 'react-router-dom';
import { Missing } from '../../../../components/core/Missing';
import { ClickableTableRow } from '../../../../components/core/Table/ClickableTableRow';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import {
  AllCashPlansQuery,
  useCashPlanVerificationStatusChoicesQuery,
} from '../../../../__generated__/graphql';

interface FspTableRowProps {
  plan: AllCashPlansQuery['allCashPlans']['edges'][number]['node'];
  canViewDetails: boolean;
}

export const FspTableRow = ({
  plan,
  canViewDetails,
}: FspTableRowProps): React.ReactElement => {
  const history = useHistory();
  const businessArea = useBusinessArea();
  const paymentVerificationPlanPath = `/${businessArea}/payment-verification/${plan.id}`;
  const handleClick = (): void => {
    history.push(paymentVerificationPlanPath);
  };
  const {
    data: statusChoicesData,
  } = useCashPlanVerificationStatusChoicesQuery();

  if (!statusChoicesData) return null;

  return (
    <ClickableTableRow
      hover
      onClick={canViewDetails ? handleClick : undefined}
      role='checkbox'
      key={plan.id}
    >
      <TableCell align='left'>
        <Missing />
      </TableCell>
      <TableCell align='left'>
        <Missing />
      </TableCell>
      <TableCell align='left'>
        <Missing />
      </TableCell>
      <TableCell align='left'>
        <Missing />
      </TableCell>
      <TableCell>
        <Box display='flex' align-items='center'>
          <IconButton
            onClick={() => {
              console.log('DELETE');
            }}
          >
            <Delete />
          </IconButton>
          <IconButton
            onClick={() => {
              console.log('EDIT');
            }}
          >
            <Edit />
          </IconButton>
        </Box>
      </TableCell>
    </ClickableTableRow>
  );
};
