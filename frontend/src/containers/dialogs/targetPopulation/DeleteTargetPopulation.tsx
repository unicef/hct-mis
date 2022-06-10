import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Typography,
} from '@mui/material';
import { Formik } from 'formik';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { useSnackbar } from '../../../hooks/useSnackBar';
import { useDeleteTargetPopulationMutation } from '../../../__generated__/graphql';
import { DialogDescription } from '../DialogDescription';
import { DialogFooter } from '../DialogFooter';
import { DialogTitleWrapper } from '../DialogTitleWrapper';

export interface DeleteTargetPopulation {
  open: boolean;
  setOpen: Function;
}

export function DeleteTargetPopulation({
  open,
  setOpen,
  targetPopulationId,
}): React.ReactElement {
  const { t } = useTranslation();
  const [mutate] = useDeleteTargetPopulationMutation();
  const { showMessage } = useSnackbar();
  const businessArea = useBusinessArea();
  const initialValues = {
    id: targetPopulationId,
  };
  return (
    <Dialog
      open={open}
      onClose={() => setOpen(false)}
      scroll='paper'
      aria-labelledby='form-dialog-title'
    >
      <Formik
        validationSchema={null}
        initialValues={initialValues}
        onSubmit={async () => {
          await mutate({
            variables: { input: { targetId: targetPopulationId } },
          });
          setOpen(false);
          showMessage('Target Population Deleted', {
            pathname: `/${businessArea}/target-population/`,
            historyMethod: 'push',
          });
        }}
      >
        {({ submitForm }) => (
          <>
            <DialogTitleWrapper>
              <DialogTitle id='scroll-dialog-title'>
                <Typography variant='h6'>
                  {t('Delete Target Population')}
                </Typography>
              </DialogTitle>
            </DialogTitleWrapper>
            <DialogContent>
              <DialogDescription>
                {t('Are you sure you want to delete this Target Population?')}
              </DialogDescription>
            </DialogContent>
            <DialogFooter>
              <DialogActions>
                <Button onClick={() => setOpen(false)}>{t('CANCEL')}</Button>
                <Button
                  type='submit'
                  color='primary'
                  variant='contained'
                  onClick={submitForm}
                >
                  {t('Delete')}
                </Button>
              </DialogActions>
            </DialogFooter>
          </>
        )}
      </Formik>
    </Dialog>
  );
}
