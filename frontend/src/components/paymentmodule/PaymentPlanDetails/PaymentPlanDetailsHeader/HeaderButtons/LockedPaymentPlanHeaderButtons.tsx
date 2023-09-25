import { Box } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { usePaymentPlanAction } from '../../../../../hooks/usePaymentPlanAction';
import { useSnackbar } from '../../../../../hooks/useSnackBar';
import { Action, PaymentPlanQuery } from '../../../../../__generated__/graphql';
import { LoadingButton } from '../../../../core/LoadingButton';
import { LockFspPaymentPlan } from '../LockFspPaymentPlan';

export interface LockedPaymentPlanHeaderButtonsProps {
  paymentPlan: PaymentPlanQuery['paymentPlan'];
  canUnlock: boolean;
  permissions: string[];
}

export const LockedPaymentPlanHeaderButtons = ({
  paymentPlan,
  canUnlock,
  permissions,
}: LockedPaymentPlanHeaderButtonsProps): React.ReactElement => {
  const { t } = useTranslation();
  const { id } = paymentPlan;
  const { showMessage } = useSnackbar();
  const {
    mutatePaymentPlanAction: unlock,
    loading: loadingUnlock,
  } = usePaymentPlanAction(Action.Unlock, id, () =>
    showMessage(t('Payment Plan has been unlocked.')),
  );

  return (
    <Box display='flex' alignItems='center'>
      {canUnlock && (
        <Box m={2}>
          <LoadingButton
            loading={loadingUnlock}
            variant='outlined'
            color='primary'
            onClick={() => unlock()}
            data-cy='button-unlock-plan'
          >
            {t('Unlock')}
          </LoadingButton>
        </Box>
      )}
      <LockFspPaymentPlan paymentPlan={paymentPlan} permissions={permissions} />
    </Box>
  );
};
