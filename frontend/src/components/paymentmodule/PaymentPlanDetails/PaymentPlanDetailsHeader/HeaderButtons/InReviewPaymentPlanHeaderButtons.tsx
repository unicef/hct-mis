import { Box } from '@mui/material';
import React from 'react';
import { PaymentPlanQuery } from '../../../../../__generated__/graphql';
import { MarkAsReleasedPaymentPlan } from '../MarkAsReleasedPaymentPlan';
import { RejectPaymentPlan } from '../RejectPaymentPlan';

export interface InReviewPaymentPlanHeaderButtonsProps {
  paymentPlan: PaymentPlanQuery['paymentPlan'];
  canReject: boolean;
  canMarkAsReleased: boolean;
}

export function InReviewPaymentPlanHeaderButtons({
  paymentPlan,
  canReject,
  canMarkAsReleased,
}: InReviewPaymentPlanHeaderButtonsProps): React.ReactElement {
  return (
    <Box display="flex" alignItems="center">
      {canReject && <RejectPaymentPlan paymentPlanId={paymentPlan.id} />}
      {canMarkAsReleased && (
        <MarkAsReleasedPaymentPlan paymentPlan={paymentPlan} />
      )}
    </Box>
  );
}
