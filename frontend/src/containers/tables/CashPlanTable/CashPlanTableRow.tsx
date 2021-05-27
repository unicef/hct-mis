import styled from 'styled-components';
import TableCell from '@material-ui/core/TableCell';
import React from 'react';
import {useHistory} from 'react-router-dom';
import {CashPlanNode} from '../../../__generated__/graphql';
import {useBusinessArea} from '../../../hooks/useBusinessArea';
import {ClickableTableRow} from '../../../components/table/ClickableTableRow';
import {StatusBox} from '../../../components/StatusBox';
import {cashPlanStatusToColor, renderSomethingOrDash,} from '../../../utils/utils';
import {UniversalMoment} from '../../../components/UniversalMoment';

const StatusContainer = styled.div`
  min-width: 120px;
  max-width: 200px;
`;

interface CashPlanTableRowProps {
  cashPlan: CashPlanNode;
}

export function CashPlanTableRow({
  cashPlan,
}: CashPlanTableRowProps): React.ReactElement {
  const history = useHistory();
  const businessArea = useBusinessArea();
  const handleClick = (): void => {
    const path = `/${businessArea}/cashplans/${cashPlan.id}`;
    history.push(path);
  };
  return (
    <ClickableTableRow
      hover
      onClick={handleClick}
      role='checkbox'
      key={cashPlan.id}
    >
      <TableCell align='left'>
        <div
          style={{
            textOverflow: 'ellipsis',
          }}
        >
          {cashPlan.caId}
        </div>
      </TableCell>
      <TableCell align='left'>
        <StatusContainer>
          <StatusBox
            status={cashPlan.status}
            statusToColor={cashPlanStatusToColor}
          />
        </StatusContainer>
      </TableCell>
      <TableCell align='right'>{cashPlan.totalNumberOfHouseholds}</TableCell>
      <TableCell align='left'>{cashPlan.assistanceMeasurement}</TableCell>
      <TableCell align='right'>
        {renderSomethingOrDash(
          cashPlan?.totalEntitledQuantity?.toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          }),
        )}
      </TableCell>
      <TableCell align='right'>
        {renderSomethingOrDash(
          cashPlan?.totalDeliveredQuantity?.toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          }),
        )}
      </TableCell>
      <TableCell align='right'>
        {renderSomethingOrDash(
          cashPlan?.totalUndeliveredQuantity?.toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          }),
        )}
      </TableCell>
      <TableCell align='left'>
        <UniversalMoment>{cashPlan.dispersionDate}</UniversalMoment>
      </TableCell>
    </ClickableTableRow>
  );
}
