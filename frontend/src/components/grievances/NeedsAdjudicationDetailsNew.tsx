import {
  Box,
  Button,
  Checkbox,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from '@material-ui/core';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useHistory } from 'react-router-dom';
import {
  GrievanceTicketDocument,
  GrievanceTicketQuery,
  useApproveNeedsAdjudicationMutation,
} from '../../__generated__/graphql';
import { useBaseUrl } from '../../hooks/useBaseUrl';
import { GRIEVANCE_TICKET_STATES } from '../../utils/constants';
import { BlackLink } from '../core/BlackLink';
import { useConfirmation } from '../core/ConfirmationDialog';
import { Title } from '../core/Title';
import { UniversalMoment } from '../core/UniversalMoment';
import {
  ApproveBox,
  StyledTable,
} from './GrievancesApproveSection/ApproveSectionStyles';
import {useSnackbar} from "../../hooks/useSnackBar";

export function NeedsAdjudicationDetailsNew({
  ticket,
  canApprove,
}: {
  ticket: GrievanceTicketQuery['grievanceTicket'];
  canApprove: boolean;
}): React.ReactElement {
  const { t } = useTranslation();
  const { baseUrl, isAllPrograms } = useBaseUrl();
  const history = useHistory();
  const confirm = useConfirmation();
  const { showMessage } = useSnackbar();

  const [approve] = useApproveNeedsAdjudicationMutation({
    refetchQueries: () => [
      {
        query: GrievanceTicketDocument,
        variables: { id: ticket.id },
      },
    ],
  });
  const details = ticket.needsAdjudicationTicketDetails;
  const initialIds = details.selectedIndividuals.map((el) => el.id);

  const [selectedDuplicates, setSelectedDuplicates] = useState(initialIds);
  const [isEditMode, setIsEditMode] = useState(false);

  const handleChecked = (id: string): void => {
    let newSelected = [...selectedDuplicates];
    if (selectedDuplicates.includes(id)) {
      newSelected = newSelected.filter((el) => el !== id);
    } else {
      newSelected.push(id);
    }
    setSelectedDuplicates(newSelected);
  };

  const allSelected = (): boolean => {
    let tableItemsCount = details.possibleDuplicates.length;
    if (details.goldenRecordsIndividual?.id) {
      tableItemsCount += 1;
    }
    return tableItemsCount === selectedDuplicates.length;
  };

  const getConfirmationText = (): string => {
    let confirmationText = '';
    if (selectedDuplicates.length === 1) {
      confirmationText = t(
        'Are you sure you want to mark this record as duplicate? It will be removed from Golden Records upon ticket closure.',
      );
    }
    if (selectedDuplicates.length > 1) {
      confirmationText = t(
        'Are you sure you want to mark these records as duplicates? They will be removed from Golden Records upon ticket closure.',
      );
    }

    if (allSelected()) {
      confirmationText = t('You cannot mark all individuals as duplicates');
    }
    return confirmationText;
  };
  const isApproved = !!details.selectedIndividual;
  const isEditable = isEditMode || !isApproved;

  const isApproveDisabled = (): boolean => {
    return (
      ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL ||
      !selectedDuplicates.length
    );
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

  const getPossibleDuplicateSimilarity = (
    possibleDuplicate,
  ): number | string => {
    const { extraData, goldenRecordsIndividual } = details;
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
            checked={selectedDuplicates.includes(possibleDuplicate?.id)}
            onChange={() => handleChecked(possibleDuplicate?.id)}
          />
        </TableCell>
        <TableCell align='left'>
          {!isAllPrograms ? (
            <BlackLink
              to={`/${baseUrl}/population/individuals/${possibleDuplicate?.id}`}
            >
              {possibleDuplicate?.unicefId}
            </BlackLink>
          ) : (
            <span>{possibleDuplicate?.unicefId}</span>
          )}
        </TableCell>
        <TableCell align='left'>
          {!isAllPrograms ? (
            <BlackLink
              to={`/${baseUrl}/population/household/${possibleDuplicate?.household?.id}`}
            >
              {possibleDuplicate?.household?.unicefId || '-'}
            </BlackLink>
          ) : (
            <span>{possibleDuplicate?.household?.unicefId || '-'}</span>
          )}
        </TableCell>
        <TableCell align='left'>{possibleDuplicate?.fullName}</TableCell>
        <TableCell align='left'>{possibleDuplicate?.sex}</TableCell>
        <TableCell align='left'>
          <UniversalMoment>{possibleDuplicate?.birthDate}</UniversalMoment>
        </TableCell>
        <TableCell align='left'>
          {getPossibleDuplicateSimilarity(possibleDuplicate)}
        </TableCell>
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
          {possibleDuplicate?.household?.admin2?.name}
        </TableCell>
        <TableCell align='left'>
          {possibleDuplicate?.household?.village}
        </TableCell>
      </TableRow>
    );
  };

  return (
    <ApproveBox>
      <Title>
        <Box display='flex' justifyContent='space-between'>
          <Typography variant='h6'>
            {t('Needs Adjudication Details')}
          </Typography>
          <Box gridGap={24} display='flex'>
            <Button
              onClick={() =>
                history.push({
                  pathname: `/${baseUrl}/grievance/new-ticket`,
                  state: { linkedTicketId: ticket.id },
                })
              }
              variant='outlined'
              color='primary'
              data-cy='button-create-linked-ticket'
            >
              {t('Create Linked Ticket')}
            </Button>
            {!isEditable && (
              <Button
                variant='outlined'
                color='primary'
                data-cy='button-edit'
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
                data-cy='button-mark-duplicate'
                onClick={() =>
                  confirm({
                    content: getConfirmationText(),
                    disabled: allSelected(),
                  }).then(async () => {
                    try {
                      await approve({
                        variables: {
                          grievanceTicketId: ticket.id,
                          selectedIndividualIds: selectedDuplicates,
                        },
                      });
                    } catch(e) {
                      e.graphQLErrors.map((x) => showMessage(x.message));
                    }
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
            <TableCell data-cy='table-cell-individual-id' align='left'>
              {t('Individual ID')}
            </TableCell>
            <TableCell data-cy='table-cell-household-id' align='left'>
              {t('Household ID')}
            </TableCell>
            <TableCell data-cy='table-cell-full-name' align='left'>
              {t('Full Name')}
            </TableCell>
            <TableCell data-cy='table-cell-gender' align='left'>
              {t('Gender')}
            </TableCell>
            <TableCell data-cy='table-cell-date-of-birth' align='left'>
              {t('Date of Birth')}
            </TableCell>
            <TableCell data-cy='table-cell-similarity-score' align='left'>
              {t('Similarity Score')}
            </TableCell>
            <TableCell data-cy='table-cell-last-registration-date' align='left'>
              {t('Last Registration Date')}
            </TableCell>
            <TableCell data-cy='table-cell-doc-type' align='left'>
              {t('Doc Type')}
            </TableCell>
            <TableCell data-cy='table-cell-doc-number' align='left'>
              {t('Doc #')}
            </TableCell>
            <TableCell data-cy='table-cell-admin-level2' align='left'>
              {t('Admin Level 2')}
            </TableCell>
            <TableCell data-cy='table-cell-village' align='left'>
              {t('Village')}
            </TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          <TableRow>
            <TableCell align='left'>
              <Checkbox
                color='primary'
                data-cy='checkbox-individual'
                disabled={
                  !isEditable ||
                  ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL
                }
                checked={selectedDuplicates.includes(
                  details.goldenRecordsIndividual?.id,
                )}
                onChange={() =>
                  handleChecked(details.goldenRecordsIndividual?.id)
                }
              />
            </TableCell>

            <TableCell align='left'>
              {!isAllPrograms ? (
                <BlackLink
                  to={`/${baseUrl}/population/individuals/${details.goldenRecordsIndividual?.id}`}
                >
                  {details.goldenRecordsIndividual?.unicefId}
                </BlackLink>
              ) : (
                <span>{details.goldenRecordsIndividual?.unicefId}</span>
              )}
            </TableCell>
            <TableCell align='left'>
              {!isAllPrograms ? (
                <BlackLink
                  to={`/${baseUrl}/population/household/${details.goldenRecordsIndividual?.household?.id}`}
                >
                  {details.goldenRecordsIndividual?.household?.unicefId || '-'}
                </BlackLink>
              ) : (
                <span>
                  {details.goldenRecordsIndividual?.household?.unicefId || '-'}
                </span>
              )}
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
              {details.goldenRecordsIndividual?.household?.admin2?.name}
            </TableCell>
            <TableCell align='left'>
              {details.goldenRecordsIndividual?.household?.village}
            </TableCell>
          </TableRow>
          {details.possibleDuplicates.map((el) =>
            renderPossibleDuplicateRow(el),
          )}
        </TableBody>
      </StyledTable>
    </ApproveBox>
  );
}
