import { Title } from '@core/Title';
import { GrievanceTicketQuery } from '@generated/graphql';
import { Box, Typography } from '@mui/material';
import { GRIEVANCE_TICKET_STATES } from '@utils/constants';
import { arraysHaveSameContent } from '@utils/utils';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { ApproveBox } from '../GrievancesApproveSection/ApproveSectionStyles';
import { NeedsAdjudicationActions } from './NeedsAdjudicationActions';
import { NeedsAdjudicationTable } from './NeedsAdjudicationTable';

export const NeedsAdjudicationDetailsNew = ({
  ticket,
  canApprove,
}: {
  ticket: GrievanceTicketQuery['grievanceTicket'];
  canApprove: boolean;
}): React.ReactElement => {
  const { t } = useTranslation();
  const details = ticket.needsAdjudicationTicketDetails;
  const {
    extraData,
    goldenRecordsIndividual,
    possibleDuplicate,
    possibleDuplicates,
  } = details;
  const [selectedIndividualIds, setSelectedIndividualIds] = useState([]);
  const [isEditMode, setIsEditMode] = useState(false);

  const findRecord = (itemId) => (record) => record.hitId === itemId;

  const getSimilarity = (records, individualId): number =>
    records?.find(findRecord(individualId))?.score;

  const getGoldenRecordSimilarity = (): number | string => {
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

  const isApproved = !!details.selectedIndividual;
  const isEditable = isEditMode || !isApproved;

  const isTicketForApproval =
    ticket.status === GRIEVANCE_TICKET_STATES.FOR_APPROVAL;

  const { selectedDuplicates, selectedDistinct } =
    ticket.needsAdjudicationTicketDetails;

  const markedDuplicateInPossibleDuplicates = selectedDuplicates
    .map((el) => el.id)
    .filter((id) => possibleDuplicates.map((el) => el.id).includes(id));

  const markedDistinctInPossibleDuplicates = selectedDistinct
    .map((el) => el.id)
    .filter((id) => possibleDuplicates.map((el) => el.id).includes(id));

  return (
    <ApproveBox>
      <Title>
        <Box display="flex" justifyContent="space-between">
          <Typography variant="h6">
            {t('Needs Adjudication Details')}
          </Typography>
        </Box>
      </Title>
      <NeedsAdjudicationActions
        ticket={ticket}
        isEditable={isEditable}
        canApprove={canApprove}
        isTicketForApproval={isTicketForApproval}
        selectedIndividualIds={selectedIndividualIds}
        setIsEditMode={setIsEditMode}
      />
      <NeedsAdjudicationTable
        ticket={ticket}
        selectedIndividualIds={selectedIndividualIds}
        setSelectedIndividualIds={setSelectedIndividualIds}
        isEditable={isEditable}
        markedDuplicateInPossibleDuplicates={
          markedDuplicateInPossibleDuplicates
        }
        markedDistinctInPossibleDuplicates={markedDistinctInPossibleDuplicates}
        getGoldenRecordSimilarity={getGoldenRecordSimilarity}
        getPossibleDuplicateSimilarity={getPossibleDuplicateSimilarity}
      />
    </ApproveBox>
  );
};
