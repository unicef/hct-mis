import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from '@material-ui/core';
import { Field, Formik } from 'formik';
import { useDebounce } from '../../../hooks/useDebounce';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import {
  GrievanceTicketDocument,
  ProgramNode,
  useAllProgramsQuery,
  useReassignRoleGrievanceMutation,
} from '../../../__generated__/graphql';
import { FormikCheckboxField } from '../../../shared/Formik/FormikCheckboxField';
import { LookUpIndividualFilters } from '../LookUpIndividualTable/LookUpIndividualFilters';
import { LookUpIndividualTable } from '../LookUpIndividualTable/LookUpIndividualTable';
import { useSnackbar } from '../../../hooks/useSnackBar';

const DialogFooter = styled.div`
  padding: 12px 16px;
  margin: 0;
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  text-align: right;
`;
const DialogTitleWrapper = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
`;

export const LookUpReassignRoleModal = ({
  onValueChange,
  initialValues,
  lookUpDialogOpen,
  setLookUpDialogOpen,
  ticket,
  selectedIndividual,
  selectedHousehold,
  setSelectedIndividual,
  setSelectedHousehold,
}): React.ReactElement => {
  const { id } = useParams();
  const { showMessage } = useSnackbar();
  const [mutate] = useReassignRoleGrievanceMutation();
  const [filterIndividual, setFilterIndividual] = useState({
    search: '',
    program: '',
    lastRegistrationDate: { min: undefined, max: undefined },
    residenceStatus: '',
    admin2: '',
    sex: '',
  });
  const debouncedFilterIndividual = useDebounce(filterIndividual, 500);
  const businessArea = useBusinessArea();
  const { data, loading } = useAllProgramsQuery({
    variables: { businessArea },
  });

  if (loading) return null;

  const { allPrograms } = data;
  const programs = allPrograms.edges.map((edge) => edge.node);

  const handleCancel = (): void => {
    setLookUpDialogOpen(false);
  };
  return (
    <Formik
      initialValues={initialValues}
      onSubmit={async (values) => {
        onValueChange('selectedHousehold', values.selectedHousehold);
        onValueChange('selectedIndividual', values.selectedIndividual);
        setLookUpDialogOpen(false);
        try {
          await mutate({
            variables: {
              grievanceTicketId: id,
              householdId: values.selectedHousehold.id,
              individualId: values.selectedIndividual.id,
              role: values.role,
            },
            refetchQueries: () => [
              {
                query: GrievanceTicketDocument,
                variables: { id: ticket.id },
              },
            ],
          });
          showMessage('Role Reassigned');
        } catch (e) {
          e.graphQLErrors.map((x) => showMessage(x.message));
        }
      }}
    >
      {({ submitForm, setFieldValue, values }) => (
        <Dialog
          maxWidth='lg'
          fullWidth
          open={lookUpDialogOpen}
          onClose={() => setLookUpDialogOpen(false)}
          scroll='paper'
          aria-labelledby='form-dialog-title'
        >
          <DialogTitleWrapper>
            <DialogTitle id='scroll-dialog-title'>Reassign Role</DialogTitle>
          </DialogTitleWrapper>
          <DialogContent>
            <LookUpIndividualFilters
              programs={programs as ProgramNode[]}
              filter={debouncedFilterIndividual}
              onFilterChange={setFilterIndividual}
            />
            <LookUpIndividualTable
              filter={debouncedFilterIndividual}
              businessArea={businessArea}
              setFieldValue={setFieldValue}
              valuesInner={values}
              selectedHousehold={selectedHousehold}
              setSelectedHousehold={setSelectedHousehold}
              selectedIndividual={selectedIndividual}
              setSelectedIndividual={setSelectedIndividual}
              ticket={ticket}
            />
          </DialogContent>
          <DialogFooter>
            <DialogActions>
              <Box display='flex'>
                <Box mr={1}>
                  <Field
                    name='identityVerified'
                    label='Identity Verified*'
                    component={FormikCheckboxField}
                  />
                </Box>
                <Button onClick={() => handleCancel()}>CANCEL</Button>
                <Button
                  type='submit'
                  color='primary'
                  variant='contained'
                  onClick={submitForm}
                  disabled={values.identityVerified === false}
                  data-cy='button-submit'
                >
                  SAVE
                </Button>
              </Box>
            </DialogActions>
          </DialogFooter>
        </Dialog>
      )}
    </Formik>
  );
};
