import { Box, Button, DialogContent, DialogTitle } from '@mui/material';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Dialog } from '../../containers/dialogs/Dialog';
import { DialogActions } from '../../containers/dialogs/DialogActions';
import { DialogContainer } from '../../containers/dialogs/DialogContainer';
import { DialogFooter } from '../../containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '../../containers/dialogs/DialogTitleWrapper';
import { usePaymentRefetchQueries } from '../../hooks/usePaymentRefetchQueries';
import { useSnackbar } from '../../hooks/useSnackBar';
import { useActivateCashPlanPaymentVerificationMutation } from '../../__generated__/graphql';

export interface ActivateVerificationPlanProps {
  cashPlanVerificationId: string;
  cashPlanId: string;
}

export function ActivateVerificationPlan({
  cashPlanVerificationId,
  cashPlanId,
}: ActivateVerificationPlanProps): React.ReactElement {
  const refetchQueries = usePaymentRefetchQueries(cashPlanId);
  const { t } = useTranslation();
  const [activateDialogOpen, setActivateDialogOpen] = useState(false);

  const { showMessage } = useSnackbar();
  const [mutate] = useActivateCashPlanPaymentVerificationMutation();
  const activate = async (): Promise<void> => {
    try {
      await mutate({
        variables: { cashPlanVerificationId },
        refetchQueries,
      });
    } catch (error) {
      /* eslint-disable-next-line no-console */
      console.log('error', error?.graphQLErrors);
      if (
        error?.graphQLErrors?.[0]?.validationErrors
          ?.activateCashPlanPaymentVerification?.phone_numbers
      ) {
        showMessage(
          error?.graphQLErrors?.[0]?.validationErrors?.activateCashPlanPaymentVerification?.phone_numbers.join(
            '\n',
          ),
        );
      } else {
        showMessage(t('Error during activating.'));
      }
    }

    showMessage(t('Verification plan has been activated.'));
  };
  return (
    <>
      <Box p={2}>
        <Button
          color='primary'
          variant='contained'
          onClick={() => setActivateDialogOpen(true)}
          data-cy='button-activate-plan'
        >
          {t('ACTIVATE')}
        </Button>
      </Box>
      <Dialog
        open={activateDialogOpen}
        onClose={() => setActivateDialogOpen(false)}
        scroll='paper'
        aria-labelledby='form-dialog-title'
        maxWidth='md'
      >
        <DialogTitleWrapper>
          <DialogTitle id='scroll-dialog-title'>
            {t('Activate Verification Plan')}
          </DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogContainer>
            <Box p={5}>
              {t(
                'Are you sure you want to activate the Verification Plan for this Cash Plan?',
              )}
            </Box>
          </DialogContainer>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setActivateDialogOpen(false)}>CANCEL</Button>
            <Button
              type='submit'
              color='primary'
              variant='contained'
              onClick={() => activate()}
              data-cy='button-submit'
            >
              {t('ACTIVATE')}
            </Button>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </>
  );
}
