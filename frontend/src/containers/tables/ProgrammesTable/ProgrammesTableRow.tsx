import TableCell from '@material-ui/core/TableCell';
import React from 'react';
import { useHistory } from 'react-router-dom';
import { BlackLink } from '../../../components/core/BlackLink';
import { StatusBox } from '../../../components/core/StatusBox';
import { ClickableTableRow } from '../../../components/core/Table/ClickableTableRow';
import { UniversalMoment } from '../../../components/core/UniversalMoment';
import {
  choicesToDict,
  formatCurrency,
  programStatusToColor,
} from '../../../utils/utils';
import {
  ProgrammeChoiceDataQuery,
  ProgramNode,
} from '../../../__generated__/graphql';
import { useBaseUrl } from '../../../hooks/useBaseUrl';

interface ProgrammesTableRowProps {
  program: ProgramNode;
  choicesData: ProgrammeChoiceDataQuery;
}

export function ProgrammesTableRow({
  program,
  choicesData,
}: ProgrammesTableRowProps): React.ReactElement {
  const history = useHistory();
  const { baseUrl } = useBaseUrl();
  const programDetailsPath = `/${baseUrl}/programs/${program.id}`;
  const handleClick = (): void => {
    history.push(programDetailsPath);
  };

  const programSectorChoiceDict = choicesToDict(
    choicesData.programSectorChoices,
  );

  return (
    <ClickableTableRow
      hover
      onClick={handleClick}
      role='checkbox'
      key={program.id}
    >
      <TableCell align='left'>
        <BlackLink to={programDetailsPath}>{program.name}</BlackLink>
      </TableCell>
      <TableCell align='left'>
        <StatusBox
          status={program.status}
          statusToColor={programStatusToColor}
        />
      </TableCell>
      <TableCell align='left'>
        <UniversalMoment>{program.startDate}</UniversalMoment> -{' '}
        <UniversalMoment>{program.endDate}</UniversalMoment>
      </TableCell>
      <TableCell align='left'>
        {programSectorChoiceDict[program.sector]}
      </TableCell>
      <TableCell align='right'>{program.totalNumberOfHouseholds}</TableCell>
      <TableCell align='right'>{formatCurrency(program.budget)}</TableCell>
    </ClickableTableRow>
  );
}
