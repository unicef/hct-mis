import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from '@material-ui/core';
import { Formik } from 'formik';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { LoadingButton } from '../../core/LoadingButton';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { useSnackbar } from '../../../hooks/useSnackBar';
import { useDeleteTargetPopulationMutation } from '../../../__generated__/graphql';
import { DialogDescription } from '../../../containers/dialogs/DialogDescription';
import { DialogFooter } from '../../../containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '../../../containers/dialogs/DialogTitleWrapper';

export interface DeleteEnrollmentProps {
  open: boolean;
  setOpen: Function;
  targetPopulationId: string;
}

export const DeleteEnrollment = ({
  open,
  setOpen,
  targetPopulationId,
}: DeleteEnrollmentProps): React.ReactElement => {
  const { t } = useTranslation();
  const [mutate, { loading }] = useDeleteTargetPopulationMutation();
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
          showMessage(t('Enrollment Deleted'), {
            pathname: `/${businessArea}/target-population/`,
            historyMethod: 'push',
          });
        }}
      >
        {({ submitForm }) => (
          <>
            <DialogTitleWrapper>
              <DialogTitle>{t('Delete Enrollment')}</DialogTitle>
            </DialogTitleWrapper>
            <DialogContent>
              <DialogDescription>
                {t('Are you sure you want to delete this Enrollment?')}
              </DialogDescription>
            </DialogContent>
            <DialogFooter>
              <DialogActions>
                <Button onClick={() => setOpen(false)}>{t('CANCEL')}</Button>
                <LoadingButton
                  loading={loading}
                  type='submit'
                  color='primary'
                  variant='contained'
                  onClick={submitForm}
                >
                  {t('Delete')}
                </LoadingButton>
              </DialogActions>
            </DialogFooter>
          </>
        )}
      </Formik>
    </Dialog>
  );
};
