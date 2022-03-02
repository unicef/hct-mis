import {
  Box,
  Button,
  DialogContent,
  DialogTitle,
  Typography,
} from '@material-ui/core';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import { Dialog } from '../../containers/dialogs/Dialog';
import { DialogActions } from '../../containers/dialogs/DialogActions';
import { usePaymentRefetchQueries } from '../../hooks/usePaymentRefetchQueries';
import { useSnackbar } from '../../hooks/useSnackBar';
import { getPercentage } from '../../utils/utils';
import {
  useCashPlanQuery,
  useFinishCashPlanPaymentVerificationMutation,
} from '../../__generated__/graphql';
import { LoadingComponent } from '../core/LoadingComponent';

const DialogTitleWrapper = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
`;

const DialogFooter = styled.div`
  padding: 12px 16px;
  margin: 0;
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  text-align: right;
`;

const DialogContainer = styled.div`
  width: 700px;
`;
export interface FinishVerificationPlanProps {
  cashPlanVerificationId: string;
  cashPlanId: string;
}

export function FinishVerificationPlan({
  cashPlanVerificationId,
  cashPlanId,
}: FinishVerificationPlanProps): React.ReactElement {
  const refetchQueries = usePaymentRefetchQueries(cashPlanId);
  const { t } = useTranslation();
  const [finishDialogOpen, setFinishDialogOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const [mutate] = useFinishCashPlanPaymentVerificationMutation();
  const { id } = useParams();
  const { data, loading } = useCashPlanQuery({
    variables: { id },
  });
  if (loading) {
    return <LoadingComponent />;
  }
  if (!data) {
    return null;
  }
  const { cashPlan } = data;
  const verificationPlan = cashPlan?.verifications?.edges?.length
    ? cashPlan.verifications.edges[0].node
    : null;

  const finish = async (): Promise<void> => {
    const { errors } = await mutate({
      variables: { cashPlanVerificationId },
      refetchQueries,
    });
    if (errors) {
      showMessage(t('Error while submitting'));
      return;
    }
    showMessage(t('Verification plan has been finished'));
  };

  const beneficiariesPercent = (): string => {
    const responded = verificationPlan?.respondedCount || 0;
    const sampleSize = verificationPlan?.sampleSize;
    if (sampleSize) {
      return getPercentage(responded, sampleSize);
    }
    return null;
  };

  const grievanceTickets = (): number => {
    if (verificationPlan?.sampleSize) {
      const notReceivedTicketsCount = verificationPlan?.notReceivedCount
        ? 1
        : 0;
      const receivedWithProblemsTicketsCount = verificationPlan?.receivedWithProblemsCount
        ? 1
        : 0;
      return notReceivedTicketsCount + receivedWithProblemsTicketsCount;
    }
    return null;
  };

  return (
    <>
      <Box p={2}>
        <Button
          color='primary'
          variant='contained'
          onClick={() => setFinishDialogOpen(true)}
          data-cy='button-ed-plan'
        >
          {t('Finish')}
        </Button>
      </Box>
      <Dialog
        open={finishDialogOpen}
        onClose={() => setFinishDialogOpen(false)}
        scroll='paper'
        aria-labelledby='form-dialog-title'
      >
        <DialogTitleWrapper>
          <DialogTitle id='scroll-dialog-title'>
            {t('Finish Verification Plan')}
          </DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogContainer>
            <Box>
              {beneficiariesPercent() && (
                <Typography variant='body2' style={{ marginTop: '20px' }}>
                  {t('Only')} {beneficiariesPercent()}{' '}
                  {t(
                    'of the beneficiaries have responded to this payment verification.',
                  )}
                </Typography>
              )}
              <Typography variant='body2'>
                {t('Are you sure that you want to finish?')}
              </Typography>
              {grievanceTickets() ? (
                <Typography
                  style={{ marginTop: '20px', marginBottom: '20px' }}
                  variant='body2'
                >
                  {t('Closing this verification will generate')}{' '}
                  {grievanceTickets()} {t('grievance tickets')}.
                </Typography>
              ) : null}
            </Box>
          </DialogContainer>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setFinishDialogOpen(false)}>
              {t('CANCEL')}
            </Button>
            <Button
              type='submit'
              color='primary'
              variant='contained'
              onClick={() => finish()}
              data-cy='button-submit'
            >
              {t('FINISH')}
            </Button>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </>
  );
}
