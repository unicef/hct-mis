import { Box, Button } from '@material-ui/core';
import { EditRounded } from '@material-ui/icons';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useLocation } from 'react-router-dom';
import { PaymentPlanQuery } from '../../../../../__generated__/graphql';
import { DeletePaymentPlan } from '../DeletePaymentPlan';
import { LockPaymentPlan } from '../LockPaymentPlan';
import { useBaseUrl } from '../../../../../hooks/useBaseUrl';
import { cameThroughProgramCycle } from '../../../../../utils/utils';

export interface OpenPaymentPlanHeaderButtonsProps {
  paymentPlan: PaymentPlanQuery['paymentPlan'];
  canRemove: boolean;
  canEdit: boolean;
  canLock: boolean;
}

export const OpenPaymentPlanHeaderButtons = ({
  paymentPlan,
  canRemove,
  canEdit,
  canLock,
}: OpenPaymentPlanHeaderButtonsProps): React.ReactElement => {
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();
  const location = useLocation();
  const { id, isFollowUp, programCycle } = paymentPlan;

  const detailsPath = cameThroughProgramCycle(location)
    ? `/${baseUrl}/payment-module/program-cycles/${programCycle.id}/${
        isFollowUp ? 'followup-payment-plans' : 'payment-plans'
      }/${id}/edit`
    : `/${baseUrl}/payment-module/${
        isFollowUp ? 'followup-payment-plans' : 'payment-plans'
      }/${id}/edit`;

  return (
    <Box display='flex' alignItems='center'>
      {canRemove && <DeletePaymentPlan paymentPlan={paymentPlan} />}
      {canEdit && (
        <Box m={2}>
          <Button
            variant='outlined'
            color='primary'
            startIcon={<EditRounded />}
            component={Link}
            to={detailsPath}
          >
            {t('Edit')}
          </Button>
        </Box>
      )}
      {canLock && (
        <Box m={2}>
          <LockPaymentPlan paymentPlan={paymentPlan} />
        </Box>
      )}
    </Box>
  );
};
