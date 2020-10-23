import React from 'react';
import TableCell from '@material-ui/core/TableCell';
import { useHistory } from 'react-router-dom';
import styled from 'styled-components';
import { Checkbox, TableRow } from '@material-ui/core';
import { PaymentVerificationNodeEdge } from '../../../__generated__/graphql';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import {
  decodeIdString,
  formatCurrency,
  verificationRecordsStatusToColor,
} from '../../../utils/utils';
import { StatusBox } from '../../../components/StatusBox';

const StatusContainer = styled.div`
  min-width: 120px;
  max-width: 200px;
`;
const Pointer = styled.span`
  cursor: pointer;
`;
interface VerificationRecordsTableRowProps {
  record: PaymentVerificationNodeEdge;
  selected: Array<string>;
  checkboxClickHandler: () => void;
}

export function VerificationRecordsTableRow({
  record,
  selected,
}): React.ReactElement {
  const history = useHistory();
  const businessArea = useBusinessArea();
  const handleClick = (): void => {
    const path = `/${businessArea}/verification-records/${record.id}`;
    history.push(path);
  };

  return (
    <TableRow hover role='checkbox' key={record.id}>
      <TableCell onClick={() => handleClick()} align='left'>
        <Pointer>{decodeIdString(record.paymentRecord.id)}</Pointer>
      </TableCell>
      <TableCell align='left'>
        <StatusContainer>
          <StatusBox
            status={record.status}
            statusToColor={verificationRecordsStatusToColor}
          />
        </StatusContainer>
      </TableCell>
      <TableCell align='left'>
        {record.paymentRecord.household.headOfHousehold.fullName}
      </TableCell>
      <TableCell align='left'>
        {record.paymentRecord.household.unicefId}
      </TableCell>
      <TableCell align='right'>
        {formatCurrency(record.paymentRecord.deliveredQuantity)}
      </TableCell>
      <TableCell align='right'>
        {formatCurrency(record.receivedAmount)}
      </TableCell>
      <TableCell align='left'>
        {record.paymentRecord.household.headOfHousehold.phoneNo}
      </TableCell>
      <TableCell align='left'>
        {record.paymentRecord.household.headOfHousehold.phoneNoAlternative ||
          '-'}
      </TableCell>
    </TableRow>
  );
}
