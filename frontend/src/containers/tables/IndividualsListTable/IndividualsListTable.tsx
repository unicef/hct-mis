import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import {
  IndividualNode,
  AllIndividualsQueryVariables,
  useAllIndividualsQuery,
} from '../../../__generated__/graphql';
import { UniversalTable } from '../UniversalTable';
import { headCells } from './IndividualsListTableHeadCells';
import { IndividualsListTableRow } from './IndividualsListTableRow';

const TableWrapper = styled.div`
  padding: 20px;
`;

interface IndividualsListTableProps {
  filter;
  businessArea: string;
  canViewDetails: boolean;
}

export const IndividualsListTable = ({
  businessArea,
  filter,
  canViewDetails,
}: IndividualsListTableProps): React.ReactElement => {
  const { t } = useTranslation();
  const initialVariables = {
    age: JSON.stringify(filter.age),
    businessArea,
    sex: [filter.sex],
    search: filter.text,
    adminArea: filter.adminArea?.node?.id,
    flags: filter.flags,
  };

  return (
    <TableWrapper>
      <UniversalTable<IndividualNode, AllIndividualsQueryVariables>
        title={t('Individuals')}
        headCells={headCells}
        rowsPerPageOptions={[10, 15, 20]}
        query={useAllIndividualsQuery}
        queriedObjectName='allIndividuals'
        initialVariables={initialVariables}
        renderRow={(row) => (
          <IndividualsListTableRow
            key={row.id}
            individual={row}
            canViewDetails={canViewDetails}
          />
        )}
      />
    </TableWrapper>
  );
};
