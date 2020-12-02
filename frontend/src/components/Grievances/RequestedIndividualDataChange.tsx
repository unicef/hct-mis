import { Box, Button, Paper, Typography } from '@material-ui/core';
import styled from 'styled-components';
import React, { useState } from 'react';
import { Formik } from 'formik';
import mapKeys from 'lodash/mapKeys';
import camelCase from 'lodash/camelCase';
import { ConfirmationDialog } from '../ConfirmationDialog';
import { useSnackbar } from '../../hooks/useSnackBar';
import {
  GrievanceTicketQuery,
  useApproveIndividualDataChangeMutation,
} from '../../__generated__/graphql';
import { GRIEVANCE_TICKET_STATES } from '../../utils/constants';
import { RequestedIndividualDataChangeTable } from './RequestedIndividualDataChangeTable';

const StyledBox = styled(Paper)`
  display: flex;
  flex-direction: column;
  width: 100%;
  padding: 26px 22px;
`;

const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

export function RequestedIndividualDataChange({
  ticket,
}: {
  ticket: GrievanceTicketQuery['grievanceTicket'];
}): React.ReactElement {
  const { showMessage } = useSnackbar();
  const [isEdit, setEdit] = useState(true);
  const getConfirmationText = (allChangesLength) => {
    return `You approved ${allChangesLength || 0} change${
      allChangesLength === 1 ? '' : 's'
    }, remaining proposed changes will be automatically rejected upon ticket closure.`;
  };
  const [mutate] = useApproveIndividualDataChangeMutation();
  const individualData = {
    ...ticket.individualDataUpdateTicketDetails.individualData,
  };
  const entries = Object.entries(individualData);
  const selectedDocuments = [];
  const selectedDocumentsToRemove = [];
  // eslint-disable-next-line no-plusplus
  for (let i = 0; i < individualData?.documents?.length; i++) {
    if (individualData?.documents[i]?.approve_status) {
      selectedDocuments.push(i);
    }
  }
  // eslint-disable-next-line no-plusplus
  for (let i = 0; i < individualData?.documents_to_remove?.length; i++) {
    if (individualData?.documents_to_remove[i]?.approve_status) {
      selectedDocumentsToRemove.push(i);
    }
  }
  return (
    <Formik
      initialValues={{
        selected: entries
          .filter((row) => {
            const valueDetails = mapKeys(row[1], (v, k) => camelCase(k)) as {
              value: string;
              approveStatus: boolean;
            };
            return valueDetails.approveStatus;
          })
          .map((row) => camelCase(row[0])),
        selectedDocuments,
        selectedDocumentsToRemove,
      }}
      onSubmit={async (values) => {
        const individualApproveData = values.selected.reduce((prev, curr) => {
          // eslint-disable-next-line no-param-reassign
          prev[curr] = true;
          return prev;
        }, {});
        const approvedDocumentsToCreate = values.selectedDocuments;
        const approvedDocumentsToRemove = values.selectedDocumentsToRemove;
        try {
          await mutate({
            variables: {
              grievanceTicketId: ticket.id,
              individualApproveData: JSON.stringify(individualApproveData),
              approvedDocumentsToCreate,
              approvedDocumentsToRemove,
            },
          });
          showMessage('Changes Approved');
          setEdit(false);
        } catch (e) {
          e.graphQLErrors.map((x) => showMessage(x.message));
        }
      }}
    >
      {({ submitForm, setFieldValue, values }) => {
        const allChangesLength =
          values.selected.length +
          values.selectedDocuments.length +
          values.selectedDocumentsToRemove.length;

        return (
          <StyledBox>
            <Title>
              <Box display='flex' justifyContent='space-between'>
                <Typography variant='h6'>Requested Data Change</Typography>
                {allChangesLength && !isEdit ? (
                  <Button
                    onClick={() => setEdit(true)}
                    variant='outlined'
                    color='primary'
                  >
                    EDIT
                  </Button>
                ) : (
                  <ConfirmationDialog
                    title='Warning'
                    content={getConfirmationText(allChangesLength)}
                  >
                    {(confirm) => (
                      <Button
                        onClick={confirm(() => submitForm())}
                        variant='contained'
                        color='primary'
                        disabled={
                          ticket.status !==
                            GRIEVANCE_TICKET_STATES.FOR_APPROVAL ||
                          !allChangesLength
                        }
                      >
                        Approve
                      </Button>
                    )}
                  </ConfirmationDialog>
                )}
              </Box>
            </Title>
            <RequestedIndividualDataChangeTable
              values={values}
              ticket={ticket}
              setFieldValue={setFieldValue}
              isEdit={isEdit}
            />
          </StyledBox>
        );
      }}
    </Formik>
  );
}
