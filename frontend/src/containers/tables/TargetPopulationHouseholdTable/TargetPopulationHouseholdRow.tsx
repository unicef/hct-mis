import React from 'react';
import TableCell from '@material-ui/core/TableCell';
import { HouseholdNode } from '../../../__generated__/graphql';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { ClickableTableRow } from '../../../components/table/ClickableTableRow';
import { anon } from '../../../utils/utils';

interface TargetPopulationHouseholdTableRowProps {
  household: HouseholdNode;
}

export function TargetPopulationHouseholdTableRow({
  household,
}): React.ReactElement {
  const businessArea = useBusinessArea();

  const handleClick = (): void => {
    const path = `/${businessArea}/population/household/${household.id}`;
    const win = window.open(path, '_blank');
    if (win != null) {
      win.focus();
    }
  };
  return (
    <ClickableTableRow
      hover
      onClick={handleClick}
      role='checkbox'
      key={household.id}
    >
      <TableCell align='left'>{household.unicefId}</TableCell>
      <TableCell align='left'>{`${anon(
        household.headOfHousehold.givenName,
        true,
      )} ${anon(household.headOfHousehold.familyName, true)}`}</TableCell>
      <TableCell align='left'>{household.size}</TableCell>
      <TableCell align='left'>{household.adminArea?.title || '-'}</TableCell>
      <TableCell align='left'>
        {household.selection?.vulnerabilityScore || '-'}
      </TableCell>
    </ClickableTableRow>
  );
}
