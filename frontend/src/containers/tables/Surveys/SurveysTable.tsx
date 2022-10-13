import React, { ReactElement } from 'react';
import { TableWrapper } from '../../../components/core/TableWrapper';
import { decodeIdString } from '../../../utils/utils';
import {
  AllFeedbacksQueryVariables,
  FeedbackNode,
  useAllFeedbacksQuery,
} from '../../../__generated__/graphql';
import { UniversalTable } from '../UniversalTable';
import { headCells } from './SurveysTableHeadCells';
import { SurveysTableRow } from './SurveysTableRow';

interface SurveysTableProps {
  filter;
  businessArea: string;
  canViewDetails: boolean;
}

export const SurveysTable = ({
  filter,
  businessArea,
  canViewDetails,
}: SurveysTableProps): ReactElement => {
  const initialVariables: AllFeedbacksQueryVariables = {
    feedbackId: filter.feedbackId,
    issueType: filter.issueType || '',
    createdBy: decodeIdString(filter.createdBy) || '',
    createdAtRange: filter.createdAtRange
      ? JSON.stringify(filter.createdAtRange)
      : '',
    businessAreaSlug: businessArea,
  };
  return (
    <TableWrapper>
      <UniversalTable<FeedbackNode, AllFeedbacksQueryVariables>
        headCells={headCells}
        rowsPerPageOptions={[10, 15, 20]}
        query={useAllFeedbacksQuery}
        queriedObjectName='allFeedbacks'
        defaultOrderBy='createdAt'
        defaultOrderDirection='desc'
        initialVariables={initialVariables}
        renderRow={(row) => (
          <SurveysTableRow
            key={row.id}
            feedback={row}
            canViewDetails={canViewDetails}
          />
        )}
      />
    </TableWrapper>
  );
};
