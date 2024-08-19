import { ProgramQuery } from '@generated/graphql';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import React, { ReactElement, useState } from 'react';
import { ClickableTableRow } from '@core/Table/ClickableTableRow';
import TableCell from '@mui/material/TableCell';
import { UniversalMoment } from '@core/UniversalMoment';
import { StatusBox } from '@core/StatusBox';
import { programCycleStatusToColor } from '@utils/utils';
import headCells from '@containers/tables/ProgramCycle/HeadCells';
import { AddNewProgramCycle } from '@containers/tables/ProgramCycle/NewProgramCycle/AddNewProgramCycle';
import { DeleteProgramCycle } from '@containers/tables/ProgramCycle/DeleteProgramCycle';
import { EditProgramCycle } from '@containers/tables/ProgramCycle/EditProgramCycle';
import { useQuery } from '@tanstack/react-query';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { fetchProgramCycles, ProgramCycle } from '@api/programCycleApi';
import { BlackLink } from '@core/BlackLink';
import { usePermissions } from '@hooks/usePermissions';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';

interface ProgramCycleTableProps {
  program: ProgramQuery['program'];
}

export const ProgramCycleTable = ({ program }: ProgramCycleTableProps) => {
  const [queryVariables, setQueryVariables] = useState({
    offset: 0,
    limit: 5,
    ordering: 'created_at',
  });
  const { businessArea, baseUrl } = useBaseUrl();
  const permissions = usePermissions();
  const canCreateProgramCycle =
    program.status !== 'DRAFT' &&
    hasPermissions(PERMISSIONS.PM_PROGRAMME_CYCLE_CREATE, permissions);

  const { data, error, isLoading } = useQuery({
    queryKey: ['programCycles', businessArea, program.id, queryVariables],
    queryFn: async () => {
      return fetchProgramCycles(businessArea, program.id, queryVariables);
    },
  });

  const renderRow = (row: ProgramCycle): ReactElement => {
    const detailsUrl = `/${baseUrl}/payment-module/program-cycles/${row.id}`;
    const canEditProgramCycle =
      (row.status === 'Draft' || row.status === 'Active') &&
      hasPermissions(PERMISSIONS.PM_PROGRAMME_CYCLE_UPDATE, permissions);
    const canDeleteProgramCycle =
      row.status === 'Draft' &&
      data.results.length > 1 &&
      hasPermissions(PERMISSIONS.PM_PROGRAMME_CYCLE_DELETE, permissions);
    return (
      <ClickableTableRow key={row.id} data-cy={`program-cycle-row-${row.id}`}>
        <TableCell data-cy="program-cycle-title">
          <BlackLink to={detailsUrl}>{row.title}</BlackLink>
        </TableCell>
        <TableCell data-cy={`program-cycle-status-${row.id}`}>
          <StatusBox
            status={row.status}
            statusToColor={programCycleStatusToColor}
          />
        </TableCell>
        <TableCell data-cy={`program-cycle-total-entitled-quantity-${row.id}`}>
          {row.total_entitled_quantity_usd || '-'}
        </TableCell>
        <TableCell
          data-cy={`program-cycle-total-undelivered-quantity-${row.id}`}
        >
          {row.total_undelivered_quantity_usd || '-'}
        </TableCell>
        <TableCell data-cy={`program-cycle-total-delivered-quantity-${row.id}`}>
          {row.total_delivered_quantity_usd || '-'}
        </TableCell>
        <TableCell data-cy={`program-cycle-start-date-${row.id}`}>
          <UniversalMoment>{row.start_date}</UniversalMoment>
        </TableCell>
        <TableCell data-cy={`program-cycle-end-date-${row.id}`}>
          <UniversalMoment>{row.end_date}</UniversalMoment>
        </TableCell>

        <TableCell data-cy={`program-cycle-details-btn-${row.id}`}>
          {program.status === 'ACTIVE' && (
            <>
              {canEditProgramCycle && (
                <EditProgramCycle program={program} programCycle={row} />
              )}

              {canDeleteProgramCycle && (
                <DeleteProgramCycle program={program} programCycle={row} />
              )}
            </>
          )}
        </TableCell>
      </ClickableTableRow>
    );
  };

  if (isLoading) {
    return null;
  }

  const actions = [];

  if (canCreateProgramCycle) {
    actions.push(
      <AddNewProgramCycle
        key="add-new"
        program={program}
        programCycles={data.results}
      />,
    );
  }

  return (
    <UniversalRestTable
      title="Programme Cycles"
      renderRow={renderRow}
      headCells={headCells}
      data={data}
      error={error}
      isLoading={isLoading}
      queryVariables={queryVariables}
      setQueryVariables={setQueryVariables}
      actions={actions}
    />
  );
};
