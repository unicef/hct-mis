import React from 'react';
import {
  Button,
  DialogContent,
  DialogTitle,
  Typography,
} from '@material-ui/core';
import styled from 'styled-components';
import { Field, Formik } from 'formik';
import * as Yup from 'yup';
import { FormikSelectField } from '../../../shared/Formik/FormikSelectField';
import { ProgrammeAutocomplete } from '../../../shared/ProgrammeAutocomplete';
import {
  useAllProgramsQuery,
  useApproveTpMutation,
} from '../../../__generated__/graphql';
import { useSnackbar } from '../../../hooks/useSnackBar';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { DialogActions } from '../DialogActions';
import { Dialog } from '../Dialog';

export interface ApproveCandidateListPropTypes {
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
  program: Yup.object().shape({
    id: Yup.string().required('Programme is required'),
  }),
});

export function ApproveCandidateList({ open, setOpen, targetPopulationId }) {
  const { data: programs } = useAllProgramsQuery({
    variables: { status: 'ACTIVE' },
  });
  const { showMessage } = useSnackbar();
  const businessArea = useBusinessArea();
  const [mutate, loading] = useApproveTpMutation();
  if (!programs) return null;
  const choices = programs.allPrograms.edges.map((program) => {
    return { ...program.node, value: program.node.id };
  });
  return (
    <Dialog
      open={open}
      onClose={() => setOpen(false)}
      scroll='paper'
      aria-labelledby='form-dialog-title'
    >
      <Formik
        validationSchema={validationSchema}
        initialValues={{ program: null }}
        onSubmit={(values) => {
          mutate({
            variables: { id: targetPopulationId, programId: values.program.id },
          }).then(() => {
            setOpen(false);
            showMessage('Programme Population Approved', {
              pathname: `/${businessArea}/target-population/${targetPopulationId}`,
            });
          });
        }}
      >
        {({ submitForm, values, setFieldValue }) => (
          <>
            <DialogTitleWrapper>
              <DialogTitle id='scroll-dialog-title'>
                <Typography variant='h6'>Close Programme Population</Typography>
              </DialogTitle>
            </DialogTitleWrapper>
            <DialogContent>
              <DialogDescription>
                Are you sure you want to approve the targeting criteria for this
                Programme Population? Once a Programme Population is{' '}
                <strong>Approved</strong> the targeting criteria will be
                permanently frozen.
              </DialogDescription>
              <DialogDescription>
                Note: You may duplicate the Programme Population target criteria
                at any time.
              </DialogDescription>
              <DialogDescription>
                Please select a Programme you would like to associate this
                Programme Population with:
              </DialogDescription>
              {values.program && values.program.individualDataNeeded ? (
                <DialogDescription>
                  <strong>
                    Warning: You can only select a programme that is compatible
                    with your filtering criteria
                  </strong>
                </DialogDescription>
              ) : null}

              <Field
                name='program'
                label='Programme'
                choices={choices}
                onChange={(e, object) => {
                  if (object) {
                    setFieldValue('program', object);
                  }
                }}
                component={ProgrammeAutocomplete}
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
                  disabled={
                    !loading ||
                    !values.program ||
                    values.program.individualDataNeeded
                  }
                  data-cy='button-target-population-close'
                >
                  Close
                </Button>
              </DialogActions>
            </DialogFooter>
          </>
        )}
      </Formik>
    </Dialog>
  );
}
