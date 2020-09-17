import React from 'react';
import * as Yup from 'yup';
import {
  Button,
  DialogContent,
  DialogTitle,
  Typography,
} from '@material-ui/core';
import styled from 'styled-components';
import { Formik, Field } from 'formik';
import { useCopyTargetPopulationMutation } from '../../../__generated__/graphql';
import { FormikTextField } from '../../../shared/Formik/FormikTextField';
import { useSnackbar } from '../../../hooks/useSnackBar';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { Dialog } from '../Dialog';
import { DialogActions } from '../DialogActions';

export interface FinalizeTargetPopulationPropTypes {
  open: boolean;
  setOpen: Function;
}

const DialogTitleWrapper = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
`;

const DialogFooter = styled.div`
  padding: 12px 16px;
  margin: 0;
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  text-align: right;
`;

const DialogDescription = styled.div`
  margin: 20px 0;
  font-size: 14px;
  color: rgba(0, 0, 0, 0.54);
`;

const validationSchema = Yup.object().shape({
  name: Yup.string().required('Name is required'),
});

interface DuplicateTargetPopulationPropTypes {
  open: boolean;
  setOpen: Function;
  targetPopulationId: string;
}

export function DuplicateTargetPopulation({
  open,
  setOpen,
  targetPopulationId,
}: DuplicateTargetPopulationPropTypes): React.ReactElement {
  const [mutate] = useCopyTargetPopulationMutation();
  const { showMessage } = useSnackbar();
  const businessArea = useBusinessArea();
  const initialValues = {
    name: '',
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
        validationSchema={validationSchema}
        initialValues={initialValues}
        onSubmit={(values) => {
          mutate({
            variables: { input: { targetPopulationData: { ...values } } },
          }).then(
            (res) => {
              setOpen(false);
              return showMessage('Target Population Duplicated', {
                pathname: `/${businessArea}/target-population/${res.data.copyTargetPopulation.targetPopulation.id}`,
                historyMethod: 'push',
              });
            },
            () => {
              return showMessage('Name already exists');
            },
          );
        }}
      >
        {({ submitForm }) => (
          <>
            <DialogTitleWrapper>
              <DialogTitle id='scroll-dialog-title'>
                <Typography variant='h6'>
                  Duplicate Target Population?
                </Typography>
              </DialogTitle>
            </DialogTitleWrapper>
            <DialogContent>
              <DialogDescription>
                Please use a unique name for the copy of this Target Population.
                <br /> <strong>Note</strong>: This duplicate will copy the
                Target Criteria of the Programme Population and update to the
                latest results from the system.
              </DialogDescription>
              <Field
                name='name'
                fullWidth
                label='Name Copy of Target Population'
                required
                variant='outlined'
                component={FormikTextField}
              />
            </DialogContent>
            <DialogFooter>
              <DialogActions>
                <Button onClick={() => setOpen(false)}>CANCEL</Button>
                <Button
                  type='submit'
                  color='primary'
                  variant='contained'
                  onClick={submitForm}
                  data-cy='button-target-population-duplicate'
                >
                  Save
                </Button>
              </DialogActions>
            </DialogFooter>
          </>
        )}
      </Formik>
    </Dialog>
  );
}
