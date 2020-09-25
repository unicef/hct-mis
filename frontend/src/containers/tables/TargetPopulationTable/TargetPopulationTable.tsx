import React, { ReactElement } from 'react';
import styled from 'styled-components';
import {
  TargetPopulationNode,
  useAllTargetPopulationsQuery,
  AllTargetPopulationsQueryVariables,
} from '../../../__generated__/graphql';
import { UniversalTable } from '../UniversalTable';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { headCells } from './TargetPopulationTableHeadCells';
import { TargetPopulationTableRow } from './TargetPopulationTableRow';

const TableWrapper = styled.div`
  padding: 20px;
`;

interface TargetPopulationProps {
  filter;
}

export const TargetPopulationTable = ({
  filter,
}: TargetPopulationProps): ReactElement => {
  const businessArea = useBusinessArea();
  const initialVariables = {
    name: filter.name,
    candidateListTotalHouseholdsMin: filter.numIndividuals.min,
    candidateListTotalHouseholdsMax: filter.numIndividuals.max,
    status: filter.status,
    businessArea,
  };
  return (
    <TableWrapper>
      <UniversalTable<TargetPopulationNode, AllTargetPopulationsQueryVariables>
        title='Target Populations'
        headCells={headCells}
        rowsPerPageOptions={[10, 15, 20]}
        query={useAllTargetPopulationsQuery}
        queriedObjectName='allTargetPopulation'
        defaultOrderBy='createdAt'
        defaultOrderDirection='desc'
        initialVariables={initialVariables}
        renderRow={(row) => (
          <TargetPopulationTableRow key={row.id} targetPopulation={row} />
        )}
      />
    </TableWrapper>
  );
};
