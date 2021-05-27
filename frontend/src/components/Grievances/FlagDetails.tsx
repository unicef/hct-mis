import {
  Box,
  Button,
  makeStyles,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from '@material-ui/core';
import styled from 'styled-components';
import React from 'react';
import moment from 'moment';
import {
  GrievanceTicketDocument,
  GrievanceTicketQuery,
  useApproveSystemFlaggingMutation,
} from '../../__generated__/graphql';
import {ConfirmationDialog} from '../ConfirmationDialog';
import {Flag} from '../Flag';
import {DATE_FORMAT} from '../../config';
import {UniversalMoment} from '../UniversalMoment';
import {GRIEVANCE_TICKET_STATES} from '../../utils/constants';
import {ViewSanctionList} from './ViewSanctionList';

const StyledBox = styled(Paper)`
  display: flex;
  flex-direction: column;
  width: 100%;
  padding: 26px 22px;
`;

const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

export function FlagDetails({
  ticket,
  canApproveFlag,
}: {
  ticket: GrievanceTicketQuery['grievanceTicket'];
  canApproveFlag: boolean;
}): React.ReactElement {
  const useStyles = makeStyles(() => ({
    table: {
      minWidth: 100,
    },
  }));
  const [approve] = useApproveSystemFlaggingMutation({
    refetchQueries: () => [
      {
        query: GrievanceTicketDocument,
        variables: { id: ticket.id },
      },
    ],
  });
  const classes = useStyles();
  const confirmationText =
    'Are you sure you want to confirm flag (sanction list match) ?';
  const removalText = 'Are you sure you want to remove the flag ?';
  const details = ticket.systemFlaggingTicketDetails;
  const isFlagConfirmed = details.approveStatus;
  return (
    <StyledBox>
      <Title>
        <Box display='flex' justifyContent='space-between'>
          <Typography variant='h6'>Flag Details</Typography>
          <Box>
            <ViewSanctionList
              referenceNumber={details.sanctionListIndividual.referenceNumber}
            />
            {canApproveFlag && (
              <ConfirmationDialog
                title='Confirmation'
                content={isFlagConfirmed ? removalText : confirmationText}
              >
                {(confirm) => (
                  <Button
                    disabled={
                      ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL
                    }
                    onClick={confirm(() =>
                      approve({
                        variables: {
                          grievanceTicketId: ticket.id,
                          approveStatus: !details.approveStatus,
                        },
                      }),
                    )}
                    variant='outlined'
                    color='primary'
                  >
                    {isFlagConfirmed ? 'REMOVE FLAG' : 'CONFIRM FLAG'}
                  </Button>
                )}
              </ConfirmationDialog>
            )}
          </Box>
        </Box>
      </Title>
      <Table className={classes.table}>
        <TableHead>
          <TableRow>
            <TableCell align='left' />
            <TableCell align='left'>Ref. No. on Sanction List</TableCell>
            <TableCell align='left'>Full Name</TableCell>
            <TableCell align='left'>Date of Birth</TableCell>
            <TableCell align='left'>National Ids</TableCell>
            <TableCell align='left'>Source</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          <TableRow>
            <TableCell align='left'>
              {details.approveStatus ? <Flag /> : ''}
            </TableCell>
            <TableCell align='left'>-</TableCell>
            <TableCell align='left'>
              {details.goldenRecordsIndividual.fullName}
            </TableCell>
            <TableCell align='left'>
              <UniversalMoment>
                {details.goldenRecordsIndividual.birthDate}
              </UniversalMoment>
            </TableCell>
            <TableCell align='left'>
              {details.goldenRecordsIndividual.documents.edges
                .filter((item) => item.node.type.type === 'NATIONAL_ID')
                .map((item) => item.node.documentNumber)
                .join(', ') || '-'}
            </TableCell>
            <TableCell align='left'>Golden Record</TableCell>
          </TableRow>
          <TableRow>
            <TableCell align='left' />
            <TableCell align='left'>
              {details.sanctionListIndividual.referenceNumber}
            </TableCell>
            <TableCell align='left'>
              {details.sanctionListIndividual.fullName}
            </TableCell>
            <TableCell align='left'>
              {details.sanctionListIndividual.datesOfBirth.edges
                .map((item) => moment(item.node.date).format(DATE_FORMAT))
                .join(', ') || '-'}
            </TableCell>
            <TableCell align='left'>
              {details.sanctionListIndividual.documents.edges
                .map((item) => item.node.documentNumber)
                .join(', ') || '-'}
            </TableCell>
            <TableCell align='left'>Sanction List</TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </StyledBox>
  );
}
