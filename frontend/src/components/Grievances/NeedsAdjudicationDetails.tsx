import {
  Box,
  Button,
  Checkbox,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from '@material-ui/core';
import { useHistory } from 'react-router-dom';
import styled from 'styled-components';
import React, { useState } from 'react';
import {
  GrievanceTicketDocument,
  GrievanceTicketQuery,
  useApproveNeedsAdjudicationMutation,
} from '../../__generated__/graphql';
import { ConfirmationDialog } from '../ConfirmationDialog';
import { UniversalMoment } from '../UniversalMoment';
import { GRIEVANCE_TICKET_STATES } from '../../utils/constants';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { BlackLink } from '../BlackLink';

const StyledBox = styled(Paper)`
  display: flex;
  flex-direction: column;
  width: 100%;
  padding: 26px 22px;
`;
const StyledTable = styled(Table)`
  && {
    min-width: 100px;
  }
`;

const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

export function NeedsAdjudicationDetails({
  ticket,
  canApprove,
}: {
  ticket: GrievanceTicketQuery['grievanceTicket'];
  canApprove: boolean;
}): React.ReactElement {
  const businessArea = useBusinessArea();
  const history = useHistory();
  const [approve] = useApproveNeedsAdjudicationMutation({
    refetchQueries: () => [
      {
        query: GrievanceTicketDocument,
        variables: { id: ticket.id },
      },
    ],
  });
  const details = ticket.needsAdjudicationTicketDetails;
  const [selectedDuplicate, setSelectedDuplicate] = useState(
    details?.selectedIndividual?.id,
  );
  const [isEditMode, setIsEditMode] = useState(false);
  const confirmationText =
    'Are you sure you want to mark this record as duplicate? It will be removed from Golden Records upon ticket closure.';
  const isApproved = !!details.selectedIndividual;
  const isEditable = isEditMode || !isApproved;

  const isApproveDisabled = (): boolean => {
    return ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL;
  };

  return (
    <StyledBox>
      <Title>
        <Box display='flex' justifyContent='space-between'>
          <Typography variant='h6'>Needs Adjudication Details</Typography>
          <Box gridGap={24} display='flex'>
            <Button
              onClick={() =>
                history.push({
                  pathname: `/${businessArea}/grievance-and-feedback/new-ticket`,
                  state: { linkedTicketId: ticket.id },
                })
              }
              variant='outlined'
              color='primary'
            >
              Create Linked Ticket
            </Button>
            {!isEditable && (
              <Button
                variant='outlined'
                color='primary'
                disabled={
                  ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL
                }
                onClick={() => setIsEditMode(true)}
              >
                Edit
              </Button>
            )}
            {isEditable && canApprove && (
              <ConfirmationDialog
                title='Confirmation'
                content={confirmationText}
              >
                {(confirm) => (
                  <Button
                    disabled={isApproveDisabled()}
                    onClick={confirm(() => {
                      approve({
                        variables: {
                          grievanceTicketId: ticket.id,
                          selectedIndividualId: selectedDuplicate,
                        },
                      });
                      setIsEditMode(false);
                    })}
                    variant='outlined'
                    color='primary'
                  >
                    mark duplicate
                  </Button>
                )}
              </ConfirmationDialog>
            )}
          </Box>
        </Box>
      </Title>
      <StyledTable>
        <TableHead>
          <TableRow>
            <TableCell align='left' />
            <TableCell align='left'>Individual ID</TableCell>
            <TableCell align='left'>Household ID</TableCell>
            <TableCell align='left'>Full Name</TableCell>
            <TableCell align='left'>Gender</TableCell>
            <TableCell align='left'>Date of Birth</TableCell>
            <TableCell align='left'>Similarity Score</TableCell>
            <TableCell align='left'>Last Registration Date</TableCell>
            <TableCell align='left'>Doc Type</TableCell>
            <TableCell align='left'>Doc #</TableCell>
            <TableCell align='left'>Admin Level 2</TableCell>
            <TableCell align='left'>Village</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          <TableRow>
            <TableCell align='left'>
              <Checkbox
                color='primary'
                disabled={
                  !isEditable ||
                  ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL
                }
                checked={
                  selectedDuplicate === details.goldenRecordsIndividual?.id
                }
                onChange={(event, checked) =>
                  setSelectedDuplicate(
                    checked ? details.goldenRecordsIndividual?.id : null,
                  )
                }
              />
            </TableCell>

            <TableCell align='left'>
              <BlackLink
                target='_blank'
                rel='noopener noreferrer'
                to={`/${businessArea}/population/individuals/${details.goldenRecordsIndividual?.id}`}
              >
                {details.goldenRecordsIndividual?.unicefId}
              </BlackLink>
            </TableCell>
            <TableCell align='left'>
              <BlackLink
                target='_blank'
                rel='noopener noreferrer'
                to={`/${businessArea}/population/household/${details.goldenRecordsIndividual?.household?.id}`}
              >
                {details.goldenRecordsIndividual?.household?.unicefId || '-'}
              </BlackLink>
            </TableCell>
            <TableCell align='left'>
              {details.goldenRecordsIndividual?.fullName}
            </TableCell>
            <TableCell align='left'>
              {details.goldenRecordsIndividual?.sex}
            </TableCell>
            <TableCell align='left'>
              <UniversalMoment>
                {details.goldenRecordsIndividual?.birthDate}
              </UniversalMoment>
            </TableCell>
            <TableCell align='left'>
              {details.goldenRecordsIndividual?.deduplicationGoldenRecordResults.find(
                (item) => item.hitId === details.possibleDuplicate?.id,
              )?.score || '-'}
            </TableCell>
            <TableCell align='left'>
              <UniversalMoment>
                {details.goldenRecordsIndividual?.lastRegistrationDate}
              </UniversalMoment>
            </TableCell>
            <TableCell align='left'>
              {
                details.goldenRecordsIndividual?.documents?.edges[0]?.node.type
                  .label
              }
            </TableCell>
            <TableCell align='left'>
              {
                details.goldenRecordsIndividual?.documents?.edges[0]?.node
                  .documentNumber
              }
            </TableCell>
            <TableCell align='left'>
              {details.goldenRecordsIndividual?.household?.admin2?.title}
            </TableCell>
            <TableCell align='left'>
              {details.goldenRecordsIndividual?.household?.village}
            </TableCell>
          </TableRow>
          <TableRow>
            <TableCell align='left'>
              <Checkbox
                color='primary'
                disabled={
                  !isEditable ||
                  ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL
                }
                checked={selectedDuplicate === details.possibleDuplicate?.id}
                onChange={(event, checked) =>
                  setSelectedDuplicate(
                    checked ? details.possibleDuplicate?.id : null,
                  )
                }
              />
            </TableCell>
            <TableCell align='left'>
              <BlackLink
                target='_blank'
                rel='noopener noreferrer'
                to={`/${businessArea}/population/individuals/${details.possibleDuplicate?.id}`}
              >
                {details.possibleDuplicate?.unicefId}
              </BlackLink>
            </TableCell>
            <TableCell align='left'>
              <BlackLink
                target='_blank'
                rel='noopener noreferrer'
                to={`/${businessArea}/population/household/${details.possibleDuplicate?.household?.id}`}
              >
                {details.possibleDuplicate?.household?.unicefId || '-'}
              </BlackLink>
            </TableCell>
            <TableCell align='left'>
              {details.possibleDuplicate?.fullName}
            </TableCell>
            <TableCell align='left'>{details.possibleDuplicate?.sex}</TableCell>
            <TableCell align='left'>
              <UniversalMoment>
                {details.possibleDuplicate?.birthDate}
              </UniversalMoment>
            </TableCell>
            <TableCell align='left'>
              {details.possibleDuplicate?.deduplicationGoldenRecordResults.find(
                (item) => item.hitId === details.goldenRecordsIndividual?.id,
              )?.score || '-'}
            </TableCell>
            <TableCell align='left'>
              <UniversalMoment>
                {details.possibleDuplicate?.lastRegistrationDate}
              </UniversalMoment>
            </TableCell>
            <TableCell align='left'>
              {details.possibleDuplicate?.documents?.edges[0]?.node.type.label}
            </TableCell>
            <TableCell align='left'>
              {
                details.possibleDuplicate?.documents?.edges[0]?.node
                  .documentNumber
              }
            </TableCell>
            <TableCell align='left'>
              {details.possibleDuplicate?.household?.admin2?.title}
            </TableCell>
            <TableCell align='left'>
              {details.possibleDuplicate?.household?.village}
            </TableCell>
          </TableRow>
        </TableBody>
      </StyledTable>
    </StyledBox>
  );
}
