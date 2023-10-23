import React, { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import {
  AllPaymentPlansForTableQueryVariables,
  PaymentPlanNode,
  useAllPaymentPlansForTableQuery,
} from '../../../../__generated__/graphql';
import { useBaseUrl } from '../../../../hooks/useBaseUrl';
import { UniversalTable } from '../../UniversalTable';
import { PaymentPlanTableRow } from './PaymentPlanTableRow';
import { headCells } from './PaymentPlansHeadCells';

interface PaymentPlansTableProps {
  filter;
  canViewDetails: boolean;
}

export const PaymentPlansTable = ({
  filter,
  canViewDetails,
}: PaymentPlansTableProps): ReactElement => {
  const { t } = useTranslation();
  const { programId, businessArea } = useBaseUrl();
  const initialVariables: AllPaymentPlansForTableQueryVariables = {
    businessArea,
    search: filter.search,
    status: filter.status,
<<<<<<< HEAD
    totalEntitledQuantityFrom: filter.totalEntitledQuantityFrom || null,
    totalEntitledQuantityTo: filter.totalEntitledQuantityTo || null,
    dispersionStartDate: filter.dispersionStartDate,
    dispersionEndDate: filter.dispersionEndDate,
=======
    totalEntitledQuantityFrom: filter.totalEntitledQuantityFrom,
    totalEntitledQuantityTo: filter.totalEntitledQuantityTo,
    dispersionStartDate: filter.dispersionStartDate || null,
    dispersionEndDate: filter.dispersionEndDate || null,
>>>>>>> 6bba15b0bb56ca008d12ef456e490df910b96e3e
    isFollowUp: filter.isFollowUp ? true : null,
    program: programId,
  };

  return (
    <UniversalTable<PaymentPlanNode, AllPaymentPlansForTableQueryVariables>
      defaultOrderBy='-createdAt'
      title={t('Payment Plans')}
      headCells={headCells}
      query={useAllPaymentPlansForTableQuery}
      queriedObjectName='allPaymentPlans'
      initialVariables={initialVariables}
      renderRow={(row) => (
        <PaymentPlanTableRow
          key={row.id}
          plan={row}
          canViewDetails={canViewDetails}
        />
      )}
    />
  );
};
