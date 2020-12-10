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
  const individualData = {
    ...ticket.individualDataUpdateTicketDetails.individualData,
  };
  let allApprovedCount = 0;
  const documents = individualData?.documents;
  const documentsToRemove = individualData.documents_to_remove;
  const flexFields = individualData.flex_fields;
  delete individualData.flex_field;
  delete individualData.documents;
  delete individualData.documents_to_remove;
  delete individualData.previous_documents;

  const entries = Object.entries(individualData);
  const entriesFlexFields = Object.entries(flexFields);
  allApprovedCount += documents.filter((el) => el.approve_status).length;
  allApprovedCount += documentsToRemove.filter((el) => el.approve_status)
    .length;
  allApprovedCount += entries.filter(
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    ([_, value]: [string, { approve_status: boolean }]) => value.approve_status,
  ).length;
  allApprovedCount += entriesFlexFields.filter(
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    ([_, value]: [string, { approve_status: boolean }]) => value.approve_status,
  ).length;

  const [isEdit, setEdit] = useState(allApprovedCount === 0);
  const getConfirmationText = (allChangesLength): string => {
    return `You approved ${allChangesLength || 0} change${
      allChangesLength === 1 ? '' : 's'
    }, remaining proposed changes will be automatically rejected upon ticket closure.`;
  };
  const [mutate] = useApproveIndividualDataChangeMutation();
  const selectedDocuments = [];
  const selectedDocumentsToRemove = [];
  // eslint-disable-next-line no-plusplus
  for (let i = 0; i < documents?.length; i++) {
    if (documents[i]?.approve_status) {
      selectedDocuments.push(i);
    }
  }
  // eslint-disable-next-line no-plusplus
  for (let i = 0; i < documentsToRemove?.length; i++) {
    if (documentsToRemove[i]?.approve_status) {
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
        selectedFlexFields: entriesFlexFields
          .filter((row) => {
            const valueDetails = mapKeys(row[1], (v, k) => camelCase(k)) as {
              value: string;
              approveStatus: boolean;
            };
            return valueDetails.approveStatus;
          })
          .map((row) => row[0]),
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
        const flexFieldsApproveData = values.selectedFlexFields.reduce(
          (prev, curr) => {
            // eslint-disable-next-line no-param-reassign
            prev[curr] = true;
            return prev;
          },
          {},
        );
        try {
          await mutate({
            variables: {
              grievanceTicketId: ticket.id,
              individualApproveData: JSON.stringify(individualApproveData),
              approvedDocumentsToCreate,
              approvedDocumentsToRemove,
              flexFieldsApproveData: JSON.stringify(flexFieldsApproveData),
            },
          });
          showMessage('Changes Approved');
          const sum =
            values.selected.length +
            values.selectedDocuments.length +
            values.selectedDocumentsToRemove.length;
          setEdit(sum === 0);
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
                    disabled={ticket.status === GRIEVANCE_TICKET_STATES.CLOSED}
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
                          ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL
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
