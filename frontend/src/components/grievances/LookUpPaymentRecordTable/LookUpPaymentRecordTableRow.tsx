import { Checkbox } from '@material-ui/core';
import TableCell from '@material-ui/core/TableCell';
import React from 'react';
import styled from 'styled-components';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import {
  formatCurrencyWithSymbol,
  verificationRecordsStatusToColor,
} from '../../../utils/utils';
import { PaymentRecordNode } from '../../../__generated__/graphql';
import { BlackLink } from '../../core/BlackLink';
import { StatusBox } from '../../core/StatusBox';
import { ClickableTableRow } from '../../core/Table/ClickableTableRow';

const StatusContainer = styled.div`
  min-width: 120px;
  max-width: 200px;
`;

interface LookUpPaymentRecordTableRowProps {
  paymentRecord: PaymentRecordNode;
  openInNewTab: boolean;
  selected: Array<string>;
  checkboxClickHandler: (
    event:
      | React.MouseEvent<HTMLButtonElement, MouseEvent>
      | React.MouseEvent<HTMLTableRowElement, MouseEvent>,
    number,
  ) => void;
}

export function LookUpPaymentRecordTableRow({
  paymentRecord,
  selected,
  checkboxClickHandler,
}: LookUpPaymentRecordTableRowProps): React.ReactElement {
  const businessArea = useBusinessArea();
  const isSelected = (name: string): boolean => selected.includes(name);
  const isItemSelected = isSelected(paymentRecord.id);
  const received = paymentRecord?.verification?.receivedAmount;
  return (
    <ClickableTableRow
      onClick={(event) => checkboxClickHandler(event, paymentRecord.id)}
      hover
      role='checkbox'
      key={paymentRecord.id}
    >
      <TableCell padding='checkbox'>
        <Checkbox
          color='primary'
          onClick={(event) => checkboxClickHandler(event, paymentRecord.id)}
          checked={isItemSelected}
          inputProps={{ 'aria-labelledby': paymentRecord.id }}
        />
      </TableCell>
      <TableCell align='left'>
        <BlackLink to={`/${businessArea}/payment-records/${paymentRecord.id}`}>
          {paymentRecord.caId}
        </BlackLink>
      </TableCell>
      <TableCell align='left'>
        {paymentRecord.verification?.status ? (
          <StatusContainer>
            <StatusBox
              status={paymentRecord.verification?.status}
              statusToColor={verificationRecordsStatusToColor}
            />
          </StatusContainer>
        ) : (
          '-'
        )}
      </TableCell>
      <TableCell align='left'>{paymentRecord.cashPlan.name}</TableCell>
      <TableCell align='right'>
        {formatCurrencyWithSymbol(
          paymentRecord.deliveredQuantity,
          paymentRecord.currency,
        )}
      </TableCell>
      <TableCell align='right'>
        {received === null || received === undefined
          ? '-'
          : formatCurrencyWithSymbol(received, paymentRecord.currency)}
      </TableCell>
    </ClickableTableRow>
  );
}
