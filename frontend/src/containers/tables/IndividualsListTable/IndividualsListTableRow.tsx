import React from 'react';
import TableCell from '@material-ui/core/TableCell';
import { useHistory } from 'react-router-dom';
import {
  IndividualNode,
  useHouseholdChoiceDataQuery,
} from '../../../__generated__/graphql';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { ClickableTableRow } from '../../../components/table/ClickableTableRow';
import { Flag } from '../../../components/Flag';
import {
  anon,
  choicesToDict,
  getAgeFromDob,
  sexToCapitalize,
} from '../../../utils/utils';
import { FlagTooltip } from '../../../components/FlagTooltip';
import { LoadingComponent } from '../../../components/LoadingComponent';
import { AnonTableCell } from '../../../components/AnonTableCell';

interface IndividualsListTableRowProps {
  individual: IndividualNode;
  canViewDetails: boolean;
  filter?;
}

export function IndividualsListTableRow({
  individual,
  canViewDetails,
  filter,
}: IndividualsListTableRowProps): React.ReactElement {
  const history = useHistory();
  const businessArea = useBusinessArea();
  const {
    data: choicesData,
    loading: choicesLoading,
  } = useHouseholdChoiceDataQuery();

  if (choicesLoading) {
    return <LoadingComponent />;
  }
  const relationshipChoicesDict = choicesToDict(
    choicesData.relationshipChoices,
  );
  let age: number | string = 'N/A';
  if (individual.birthDate) {
    age = getAgeFromDob(individual.birthDate);
  }
  const handleClick = (): void => {
    const path = `/${businessArea}/population/individuals/${individual.id}`;
    history.push(path);
  };
  return (
    <ClickableTableRow
      hover
      onClick={canViewDetails ? handleClick : undefined}
      role='checkbox'
      key={individual.id}
    >
      <TableCell align='left'>
        {individual.deduplicationGoldenRecordStatus !== 'UNIQUE' && (
          <FlagTooltip />
        )}
        {individual.sanctionListPossibleMatch && <Flag />}
      </TableCell>
      <TableCell align='left'>{individual.unicefId}</TableCell>
      <AnonTableCell anonymize={!filter?.text} align='left'>
        {individual.fullName}
      </AnonTableCell>
      <TableCell align='left'>
        {individual.household ? individual.household.unicefId : ''}
      </TableCell>
      <TableCell align='left'>
        {relationshipChoicesDict[individual.relationship]}
      </TableCell>
      <TableCell align='right'>{age}</TableCell>
      <TableCell align='left'>{sexToCapitalize(individual.sex)}</TableCell>
      <TableCell align='left'>
        {individual.household?.adminArea?.title}
      </TableCell>
    </ClickableTableRow>
  );
}
