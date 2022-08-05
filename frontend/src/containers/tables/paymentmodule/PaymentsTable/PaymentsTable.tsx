import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { UniversalTable } from '../../UniversalTable';
import {
  AllPaymentsForTableQuery,
  AllPaymentsForTableQueryVariables,
  PaymentPlanQuery,
  useAllPaymentsForTableQuery,
} from '../../../../__generated__/graphql';
import { headCells } from './PaymentsTableHeadCells';
import { PaymentsTableRow } from './PaymentsTableRow';
import { WarningTooltipTable } from './WarningTooltipTable';

const TableWrapper = styled.div`
  padding: 20px;
`;

interface PaymentsTableProps {
  businessArea: string;
  paymentPlan: PaymentPlanQuery['paymentPlan'];
  canViewDetails?: boolean;
}

export const PaymentsTable = ({
  businessArea,
  paymentPlan,
  canViewDetails = false,
}: PaymentsTableProps): React.ReactElement => {
  const { t } = useTranslation();
  const [dialogPayment, setDialogPayment] = useState<AllPaymentsForTableQuery['allPayments']['edges'][number]['node'] | null>();
  const initialVariables: AllPaymentsForTableQueryVariables = {
    businessArea,
    paymentPlanId: paymentPlan.id,
  };

  // TODO: set payment to state to pass to warning popup modal
  

  return (
    <>
      <TableWrapper>
        <UniversalTable<
          AllPaymentsForTableQuery['allPayments']['edges'][number]['node'],
          AllPaymentsForTableQueryVariables
        >
          title={t('Payments List')}
          headCells={headCells}
          query={useAllPaymentsForTableQuery}
          queriedObjectName='allPayments'
          initialVariables={initialVariables}
          defaultOrderBy='createdAt'
          defaultOrderDirection='desc'
          renderRow={(row) => (
            <PaymentsTableRow
              key={row.id}
              payment={row}
              canViewDetails={canViewDetails}
              onWarningClick={(payment) => {
                setDialogPayment(payment);
              }}
            />
          )}
        />
      </TableWrapper>
      <WarningTooltipTable
        paymentPlan={paymentPlan}
        payment={dialogPayment}
        setDialogOpen={() => setDialogPayment(null)}
      />
    </>
  );
};
