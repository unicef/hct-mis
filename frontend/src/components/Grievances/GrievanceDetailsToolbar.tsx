import { Box, Button } from '@material-ui/core';
import { useParams, Link } from 'react-router-dom';
import EditIcon from '@material-ui/icons/EditRounded';
import React from 'react';
import styled from 'styled-components';
import { MiśTheme } from '../../theme';
import { BreadCrumbsItem } from '../BreadCrumbs';
import {
  GRIEVANCE_CATEGORIES,
  GRIEVANCE_TICKET_STATES,
} from '../../utils/constants';
import { decodeIdString } from '../../utils/utils';
import {
  GrievanceTicketDocument,
  GrievanceTicketQuery,
  useGrievanceTicketStatusChangeMutation,
} from '../../__generated__/graphql';
import { PageHeader } from '../PageHeader';
import { ConfirmationDialog } from '../ConfirmationDialog';
import { useBusinessArea } from '../../hooks/useBusinessArea';

const Separator = styled.div`
  width: 1px;
  height: 28px;
  border: 1px solid
    ${({ theme }: { theme: MiśTheme }) => theme.hctPalette.lightGray};
  margin: 0 28px;
`;

export const GrievanceDetailsToolbar = ({
  ticket,
}: {
  ticket: GrievanceTicketQuery['grievanceTicket'];
}): React.ReactElement => {
  const { id } = useParams();
  const businessArea = useBusinessArea();
  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: 'Grievance and Feedback',
      to: `/${businessArea}/grievance-and-feedback/`,
    },
  ];
  const [mutate] = useGrievanceTicketStatusChangeMutation();

  const isNew = ticket.status === GRIEVANCE_TICKET_STATES.NEW;
  const isAssigned = ticket.status === GRIEVANCE_TICKET_STATES.ASSIGNED;
  const isInProgress = ticket.status === GRIEVANCE_TICKET_STATES.IN_PROGRESS;
  const isForApproval = ticket.status === GRIEVANCE_TICKET_STATES.FOR_APPROVAL;
  const isOnHold = ticket.status === GRIEVANCE_TICKET_STATES.ON_HOLD;
  const isClosed = ticket.status === GRIEVANCE_TICKET_STATES.CLOSED;
  const isEditable = !isClosed;

  const isFeedbackType =
    ticket.category.toString() === GRIEVANCE_CATEGORIES.POSITIVE_FEEDBACK ||
    ticket.category.toString() === GRIEVANCE_CATEGORIES.NEGATIVE_FEEDBACK ||
    ticket.category.toString() === GRIEVANCE_CATEGORIES.REFERRAL;

  const closingConfirmationText =
    'Are you sure you want to close the ticket ? By continuing you acknowledge that individuals in this ticket were reviewed and all were deemed unique to the system. No duplicates were found.';

  const changeState = (status): void => {
    mutate({
      variables: {
        grievanceTicketId: ticket.id,
        status,
      },
      refetchQueries: () => [
        {
          query: GrievanceTicketDocument,
          variables: { id: ticket.id },
        },
      ],
    });
  };
  return (
    <PageHeader
      title={`Ticket #${decodeIdString(id)}`}
      breadCrumbs={breadCrumbsItems}
    >
      <Box display='flex' alignItems='center'>
        {isEditable && (
          <>
            <Button
              color='primary'
              variant='outlined'
              component={Link}
              to={`/${businessArea}/grievance-and-feedback/edit-ticket/${id}`}
              startIcon={<EditIcon />}
            >
              Edit
            </Button>
            <Separator />
          </>
        )}
        {isNew && (
          <>
            <Button
              color='primary'
              variant='contained'
              onClick={() => changeState(GRIEVANCE_TICKET_STATES.ASSIGNED)}
            >
              ASSIGN TO ME
            </Button>
          </>
        )}
        {isAssigned && (
          <Button
            color='primary'
            variant='contained'
            onClick={() => changeState(GRIEVANCE_TICKET_STATES.IN_PROGRESS)}
          >
            Set to in progress
          </Button>
        )}
        {isInProgress && (
          <>
            <Box mr={3}>
              <Button
                color='primary'
                variant='outlined'
                onClick={() => changeState(GRIEVANCE_TICKET_STATES.ON_HOLD)}
              >
                Set On Hold
              </Button>
            </Box>
            <Box mr={3}>
              <Button
                color='primary'
                variant='contained'
                onClick={() =>
                  changeState(GRIEVANCE_TICKET_STATES.FOR_APPROVAL)
                }
              >
                Send For Approval
              </Button>
            </Box>
            {isFeedbackType && (
              <ConfirmationDialog
                title='Confirmation'
                content={closingConfirmationText}
                continueText='close ticket'
              >
                {(confirm) => (
                  <Button
                    color='primary'
                    variant='contained'
                    onClick={confirm(() =>
                      changeState(GRIEVANCE_TICKET_STATES.CLOSED),
                    )}
                  >
                    Close Ticket
                  </Button>
                )}
              </ConfirmationDialog>
            )}
          </>
        )}
        {isOnHold && (
          <>
            <Box mr={3}>
              <Button
                color='primary'
                variant='contained'
                onClick={() => changeState(GRIEVANCE_TICKET_STATES.IN_PROGRESS)}
              >
                Set to in progress
              </Button>
            </Box>
            <Box mr={3}>
              <Button
                color='primary'
                variant='contained'
                onClick={() =>
                  changeState(GRIEVANCE_TICKET_STATES.FOR_APPROVAL)
                }
              >
                Send For Approval
              </Button>
            </Box>
            {isFeedbackType && (
              <ConfirmationDialog
                title='Confirmation'
                content={closingConfirmationText}
                continueText='close ticket'
              >
                {(confirm) => (
                  <Button
                    color='primary'
                    variant='contained'
                    onClick={confirm(() =>
                      changeState(GRIEVANCE_TICKET_STATES.CLOSED),
                    )}
                  >
                    Close Ticket
                  </Button>
                )}
              </ConfirmationDialog>
            )}
          </>
        )}
        {isForApproval && (
          <>
            <Box mr={3}>
              <Button
                color='primary'
                variant='contained'
                onClick={() => changeState(GRIEVANCE_TICKET_STATES.IN_PROGRESS)}
              >
                Send Back
              </Button>
            </Box>
            <ConfirmationDialog
              title='Confirmation'
              content={closingConfirmationText}
              continueText='close ticket'
            >
              {(confirm) => (
                <Button
                  color='primary'
                  variant='contained'
                  onClick={confirm(() =>
                    changeState(GRIEVANCE_TICKET_STATES.CLOSED),
                  )}
                >
                  Close Ticket
                </Button>
              )}
            </ConfirmationDialog>
          </>
        )}
      </Box>
    </PageHeader>
  );
};
