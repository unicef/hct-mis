import React, {ReactElement} from 'react';
import {
  AllPaymentRecordsQueryVariables,
  CashPlanNode,
  PaymentRecordNode,
  useAllPaymentRecordsQuery,
} from '../../../__generated__/graphql';
import {UniversalTable} from '../UniversalTable';
import {headCells} from './PaymentRecordTableHeadCells';
import {PaymentRecordTableRow} from './PaymentRecordTableRow';

interface PaymentRecordTableProps {
  cashPlan: CashPlanNode;
  openInNewTab?: boolean;
  businessArea: string;
}
export function PaymentRecordTable({
  cashPlan,
  openInNewTab = false,
  businessArea,
}: PaymentRecordTableProps): ReactElement {
  const initialVariables = {
    cashPlan: cashPlan.id,
    businessArea,
  };
  return (
    <UniversalTable<PaymentRecordNode, AllPaymentRecordsQueryVariables>
      title='Payment Records'
      headCells={headCells}
      query={useAllPaymentRecordsQuery}
      queriedObjectName='allPaymentRecords'
      initialVariables={initialVariables}
      renderRow={(row) => (
        <PaymentRecordTableRow
          key={row.id}
          paymentRecord={row}
          openInNewTab={openInNewTab}
        />
      )}
    />
  );
}
