import { Box, Button } from '@material-ui/core';
import { EditRounded } from '@material-ui/icons';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import {PaymentPlanQuery, ProgramStatus} from '../../../../../__generated__/graphql';
import { DeletePaymentPlan } from '../DeletePaymentPlan';
import { LockPaymentPlan } from '../LockPaymentPlan';
import { useBaseUrl } from '../../../../../hooks/useBaseUrl';
import {useProgramContext} from "../../../../../programContext";

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
  const { id, isFollowUp } = paymentPlan;
  const { selectedProgram } = useProgramContext();

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
            to={`/${baseUrl}/payment-module/${
              isFollowUp ? 'followup-payment-plans' : 'payment-plans'
            }/${id}/edit`}
            disabled={selectedProgram?.status !== ProgramStatus.Active}
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
