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
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useHistory } from 'react-router-dom';
import styled from 'styled-components';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { GRIEVANCE_TICKET_STATES } from '../../utils/constants';
import {
  GrievanceTicketDocument,
  GrievanceTicketQuery,
  useApproveNeedsAdjudicationMutation,
} from '../../__generated__/graphql';
import { BlackLink } from '../core/BlackLink';
import { useConfirmation } from '../core/ConfirmationDialog';
import { Title } from '../core/Title';
import { UniversalMoment } from '../core/UniversalMoment';

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

export function NeedsAdjudicationDetails({
  ticket,
  canApprove,
}: {
  ticket: GrievanceTicketQuery['grievanceTicket'];
  canApprove: boolean;
}): React.ReactElement {
  const { t } = useTranslation();
  const businessArea = useBusinessArea();
  const history = useHistory();
  const confirm = useConfirmation();
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
  const confirmationText = t(
    'Are you sure you want to mark this record as duplicate? It will be removed from Golden Records upon ticket closure.',
  );
  const isApproved = !!details.selectedIndividual;
  const isEditable = isEditMode || !isApproved;

  const isApproveDisabled = (): boolean => {
    return ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL;
  };

  const findRecord = (itemId) => (record) => record.hitId === itemId;

  const getSimilarity = (records, individualId): number => {
    return records?.find(findRecord(individualId))?.score;
  };

  const getGoldenRecordSimilarity = (): number | string => {
    const { extraData, goldenRecordsIndividual, possibleDuplicate } = details;
    const individualId = possibleDuplicate?.id;
    const extraDataGoldenRecords = extraData?.goldenRecords;
    const deduplicationGoldenRecordResults =
      goldenRecordsIndividual?.deduplicationGoldenRecordResults;

    return (
      getSimilarity(extraDataGoldenRecords, individualId) ||
      getSimilarity(deduplicationGoldenRecordResults, individualId) ||
      '-'
    );
  };

  const getPossibleDuplicateSimilarity = (): number | string => {
    const { extraData, goldenRecordsIndividual, possibleDuplicate } = details;
    const individualId = goldenRecordsIndividual?.id;
    const extraDataPossibleDuplicate1 = extraData?.possibleDuplicate;
    const deduplicationGoldenRecordResults =
      possibleDuplicate?.deduplicationGoldenRecordResults;

    return (
      getSimilarity(extraDataPossibleDuplicate1, individualId) ||
      getSimilarity(deduplicationGoldenRecordResults, individualId) ||
      '-'
    );
  };

  const renderPossibleDuplicateRow = (
    possibleDuplicate,
  ): React.ReactElement => {
    return (
      <TableRow key={possibleDuplicate?.id}>
        <TableCell align='left'>
          <Checkbox
            color='primary'
            disabled={
              !isEditable ||
              ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL
            }
            checked={selectedDuplicate === possibleDuplicate?.id}
            onChange={(event, checked) =>
              setSelectedDuplicate(checked ? possibleDuplicate?.id : null)
            }
          />
        </TableCell>
        <TableCell align='left'>
          <BlackLink
            to={`/${businessArea}/population/individuals/${possibleDuplicate?.id}`}
          >
            {possibleDuplicate?.unicefId}
          </BlackLink>
        </TableCell>
        <TableCell align='left'>
          <BlackLink
            to={`/${businessArea}/population/household/${possibleDuplicate?.household?.id}`}
          >
            {possibleDuplicate?.household?.unicefId || '-'}
          </BlackLink>
        </TableCell>
        <TableCell align='left'>{possibleDuplicate?.fullName}</TableCell>
        <TableCell align='left'>{possibleDuplicate?.sex}</TableCell>
        <TableCell align='left'>
          <UniversalMoment>{possibleDuplicate?.birthDate}</UniversalMoment>
        </TableCell>
        <TableCell align='left'>{getPossibleDuplicateSimilarity()}</TableCell>
        <TableCell align='left'>
          <UniversalMoment>
            {possibleDuplicate?.lastRegistrationDate}
          </UniversalMoment>
        </TableCell>
        <TableCell align='left'>
          {possibleDuplicate?.documents?.edges[0]?.node.type.label}
        </TableCell>
        <TableCell align='left'>
          {possibleDuplicate?.documents?.edges[0]?.node.documentNumber}
        </TableCell>
        <TableCell align='left'>
          {possibleDuplicate?.household?.admin2?.title}
        </TableCell>
        <TableCell align='left'>
          {possibleDuplicate?.household?.village}
        </TableCell>
      </TableRow>
    );
  };

  return (
    <StyledBox>
      <Title>
        <Box display='flex' justifyContent='space-between'>
          <Typography variant='h6'>
            {t('Needs Adjudication Details')}
          </Typography>
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
              {t('Create Linked Ticket')}
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
                {t('Edit')}
              </Button>
            )}
            {isEditable && canApprove && (
              <Button
                disabled={isApproveDisabled()}
                onClick={() =>
                  confirm({
                    content: confirmationText,
                  }).then(() => {
                    approve({
                      variables: {
                        grievanceTicketId: ticket.id,
                        selectedIndividualId: selectedDuplicate,
                      },
                    });
                    setIsEditMode(false);
                  })
                }
                variant='outlined'
                color='primary'
              >
                {t('Mark Duplicate')}
              </Button>
            )}
          </Box>
        </Box>
      </Title>
      <StyledTable>
        <TableHead>
          <TableRow>
            <TableCell align='left' />
            <TableCell align='left'>{t('Individual ID')}</TableCell>
            <TableCell align='left'>{t('Household ID')}</TableCell>
            <TableCell align='left'>{t('Full Name')}</TableCell>
            <TableCell align='left'>{t('Gender')}</TableCell>
            <TableCell align='left'>{t('Date of Birth')}</TableCell>
            <TableCell align='left'>{t('Similarity Score')}</TableCell>
            <TableCell align='left'>{t('Last Registration Date')}</TableCell>
            <TableCell align='left'>{t('Doc Type')}</TableCell>
            <TableCell align='left'>{t('Doc #')}</TableCell>
            <TableCell align='left'>{t('Admin Level 2')}</TableCell>
            <TableCell align='left'>{t('Village')}</TableCell>
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
                to={`/${businessArea}/population/individuals/${details.goldenRecordsIndividual?.id}`}
              >
                {details.goldenRecordsIndividual?.unicefId}
              </BlackLink>
            </TableCell>
            <TableCell align='left'>
              <BlackLink
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
            <TableCell align='left'>{getGoldenRecordSimilarity()}</TableCell>
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
          {details.isMultipleDuplicatesVersion
            ? details.possibleDuplicates.map((el) =>
                renderPossibleDuplicateRow(el),
              )
            : renderPossibleDuplicateRow(details.possibleDuplicate)}
        </TableBody>
      </StyledTable>
    </StyledBox>
  );
}
