import React from 'react';
import TableCell from '@material-ui/core/TableCell';
import { useHistory } from 'react-router-dom';
import { HouseholdNode } from '../../../../../__generated__/graphql';
import { useBusinessArea } from '../../../../../hooks/useBusinessArea';
import { ClickableTableRow } from '../../../../../components/core/Table/ClickableTableRow';
import { decodeIdString, renderIndividualName } from '../../../../../utils/utils';
import { BlackLink } from '../../../../../components/core/BlackLink';

interface TargetPopulationHouseholdTableRowProps {
  household: HouseholdNode;
}

export function TargetPopulationHouseholdTableRow({
  household,
  canViewDetails,
}): React.ReactElement {
  const history = useHistory();
  const businessArea = useBusinessArea();
  const householdDetailsPath = `/${businessArea}/population/household/${household.id}`;
  const handleClick = (): void => {
    history.push(householdDetailsPath);
  };
  return (
    <ClickableTableRow
      hover
      onClick={canViewDetails ? handleClick : undefined}
      role='checkbox'
      key={household.id}
    >
      <TableCell align='left'>
        {canViewDetails ? (
          <BlackLink to={householdDetailsPath}>{household.unicefId}</BlackLink>
        ) : (
          decodeIdString(household.id)
        )}
      </TableCell>
      <TableCell align='left'>
        {renderIndividualName(household.headOfHousehold)}
      </TableCell>
      <TableCell align='left'>{household.size}</TableCell>
      <TableCell align='left'>-</TableCell>
      <TableCell align='left'>{household.address}</TableCell>
      <TableCell align='left'>{household.adminArea?.name}</TableCell>
      <TableCell align='left'>-</TableCell>
    </ClickableTableRow>
  );
}
