import TableCell from '@material-ui/core/TableCell';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { BlackLink } from '../../../../components/core/BlackLink';
import { ClickableTableRow } from '../../../../components/core/Table/ClickableTableRow';
import { WarningTooltip } from '../../../../components/core/WarningTooltip';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import {
  formatCurrencyWithSymbol,
  renderSomethingOrDash,
} from '../../../../utils/utils';
import { AllPaymentsForTableQuery } from '../../../../__generated__/graphql';

export const StyledLink = styled.div`
  color: #000;
  text-decoration: underline;
  cursor: pointer;
  display: flex;
  align-content: center;
`;

interface PaymentsTableRowProps {
  payment: AllPaymentsForTableQuery['allPayments']['edges'][number]['node'];
  canViewDetails: boolean;
  onWarningClick?: (
    payment: AllPaymentsForTableQuery['allPayments']['edges'][number]['node'],
  ) => void;
}

export const PaymentsTableRow = ({
  payment,
  canViewDetails,
  onWarningClick,
}: PaymentsTableRowProps): React.ReactElement => {
  const { t } = useTranslation();
  const businessArea = useBusinessArea();
  const householdDetailsPath = `/${businessArea}/population/household/${payment.household.id}`;
  const collectorDetailsPath = `/${businessArea}/population/individuals/${payment.collector.id}`;

  const handleDialogWarningOpen = (
    e: React.SyntheticEvent<HTMLDivElement>,
  ): void => {
    e.stopPropagation();
    onWarningClick(payment);
  };

  return (
    <ClickableTableRow hover role='checkbox' key={payment.id}>
      <TableCell align='left'>
        {(payment.paymentPlanHardConflicted ||
          payment.paymentPlanSoftConflicted) && (
          <WarningTooltip
            handleClick={(e) => handleDialogWarningOpen(e)}
            message={t(
              'This household is also included in other Payment Plans. Click this icon to view details.',
            )}
            confirmed={payment.paymentPlanHardConflicted}
          />
        )}
      </TableCell>
      <TableCell align='left'>{payment.unicefId}</TableCell>
      <TableCell align='left'>
        {canViewDetails ? (
          <BlackLink to={householdDetailsPath}>
            {payment.household.unicefId}
          </BlackLink>
        ) : (
          payment.household.unicefId
        )}
      </TableCell>
      <TableCell align='left'>{payment.household.size}</TableCell>
      <TableCell align='left'>
        {renderSomethingOrDash(payment.household.admin2?.name)}
      </TableCell>
      <TableCell align='left'>
        {canViewDetails ? (
          <BlackLink to={collectorDetailsPath}>
            {payment.collector.fullName}
          </BlackLink>
        ) : (
          payment.collector.fullName
        )}
      </TableCell>
      <TableCell align='left'>
        {payment.financialServiceProvider
          ? payment.financialServiceProvider.name
          : '-'}
      </TableCell>
      <TableCell align='left'>
        {payment.entitlementQuantityUsd > 0
          ? `${formatCurrencyWithSymbol(
              payment.entitlementQuantity,
              payment.currency,
            )} (${formatCurrencyWithSymbol(
              payment.entitlementQuantityUsd,
              'USD',
            )})`
          : '-'}
      </TableCell>
      <TableCell data-cy='delivered-quantity-cell' align='left'>
        {payment.deliveredQuantity > 0
          ? `${formatCurrencyWithSymbol(
              payment.deliveredQuantity,
              payment.currency,
            )} (${formatCurrencyWithSymbol(
              payment.deliveredQuantityUsd,
              'USD',
            )})`
          : '-'}
      </TableCell>
    </ClickableTableRow>
  );
};
