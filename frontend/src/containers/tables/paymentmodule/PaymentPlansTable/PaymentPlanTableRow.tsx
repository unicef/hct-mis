import { Box, TableCell } from '@mui/material';
import * as React from 'react';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { useCashPlanVerificationStatusChoicesQuery } from '@generated/graphql';
import { BlackLink } from '@components/core/BlackLink';
import { StatusBox } from '@components/core/StatusBox';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { UniversalMoment } from '@components/core/UniversalMoment';
import {
  formatCurrencyWithSymbol,
  paymentPlanStatusToColor,
} from '@utils/utils';
import { useBaseUrl } from '@hooks/useBaseUrl';

const StatusContainer = styled.div`
  min-width: 120px;
  max-width: 200px;
`;

interface PaymentPlanTableRowProps {
  plan;
  canViewDetails: boolean;
}

export function PaymentPlanTableRow({
  plan,
  canViewDetails,
}: PaymentPlanTableRowProps): React.ReactElement {
  const navigate = useNavigate();
  const { baseUrl } = useBaseUrl();
  const paymentPlanPath = `/${baseUrl}/payment-module/${
    plan.isFollowUp ? 'followup-payment-plans' : 'payment-plans'
  }/${plan.id}`;
  const handleClick = (): void => {
    navigate(paymentPlanPath);
  };
  const { data: statusChoicesData } =
    useCashPlanVerificationStatusChoicesQuery();

  if (!statusChoicesData) return null;

  const followUpLinks = (): React.ReactElement => {
    if (!plan.followUps?.edges?.length) return <>-</>;
    return (
      <Box display="flex" flexDirection="column">
        {plan.followUps?.edges?.map((followUp) => {
          const followUpPaymentPlanPath = `/${baseUrl}/payment-module/followup-payment-plans/${followUp?.node?.id}`;
          return (
            <Box mb={1}>
              <BlackLink key={followUp?.node?.id} to={followUpPaymentPlanPath}>
                {followUp?.node?.unicefId}
              </BlackLink>
            </Box>
          );
        })}
      </Box>
    );
  };

  return (
    <ClickableTableRow
      hover
      onClick={canViewDetails ? handleClick : undefined}
      role="checkbox"
      key={plan.id}
    >
      <TableCell align="left">
        {plan.isFollowUp ? 'Follow-up: ' : ''}
        {canViewDetails ? (
          <BlackLink to={paymentPlanPath}>{plan.unicefId}</BlackLink>
        ) : (
          plan.unicefId
        )}
      </TableCell>
      <TableCell align="left">
        <StatusContainer>
          <StatusBox
            status={plan.status}
            statusToColor={paymentPlanStatusToColor}
          />
        </StatusContainer>
      </TableCell>
      <TableCell align="left">{plan.totalHouseholdsCount || '-'}</TableCell>
      <TableCell align="left">{plan.currencyName}</TableCell>
      <TableCell align="right">
        {`${formatCurrencyWithSymbol(
          plan.totalEntitledQuantity,
          plan.currency,
        )}`}
      </TableCell>
      <TableCell align="right">
        {`${formatCurrencyWithSymbol(
          plan.totalDeliveredQuantity,
          plan.currency,
        )}`}
      </TableCell>
      <TableCell align="right">
        {`${formatCurrencyWithSymbol(
          plan.totalUndeliveredQuantity,
          plan.currency,
        )}`}
      </TableCell>
      <TableCell align="left">
        <UniversalMoment>{plan.dispersionStartDate}</UniversalMoment>
      </TableCell>
      <TableCell align="left">
        <UniversalMoment>{plan.dispersionEndDate}</UniversalMoment>
      </TableCell>
      <TableCell align="left">{followUpLinks()}</TableCell>
    </ClickableTableRow>
  );
}
