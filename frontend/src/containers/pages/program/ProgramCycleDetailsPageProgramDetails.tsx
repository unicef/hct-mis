import { Box } from '@material-ui/core';
import React from 'react';
import { useParams } from 'react-router-dom';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { PERMISSIONS, hasPermissions } from '../../../config/permissions';
import { usePermissions } from '../../../hooks/usePermissions';
import { choicesToDict, isPermissionDeniedError } from '../../../utils/utils';
import { UniversalActivityLogTable } from '../../tables/UniversalActivityLogTable';
import {
  useProgramCycleQuery,
  useProgrammeChoiceDataQuery,
} from '../../../__generated__/graphql';
import { ProgramCycleDetailsHeaderProgramDetails } from '../../../components/programs/ProgramCycleDetailsProgramDetails/ProgramCycleDetailsHeaderProgramDetails';
import { ProgramCycleDetailsProgramDetails } from '../../../components/programs/ProgramCycleDetailsProgramDetails/ProgramCycleDetailsProgramDetails';

export const ProgramCycleDetailsPageProgramDetails = (): React.ReactElement => {
  const { programCycleId } = useParams();
  const permissions = usePermissions();
  const { data: programCycleData, loading, error } = useProgramCycleQuery({
    variables: {
      id: programCycleId,
    },
    fetchPolicy: 'cache-and-network',
  });
  const {
    data: programChoiceData,
    loading: choicesLoading,
  } = useProgrammeChoiceDataQuery();

  if (loading || choicesLoading) return <LoadingComponent />;
  if (permissions === null || !programCycleData || !programChoiceData)
    return null;

  if (
    !hasPermissions(PERMISSIONS.PM_PROGRAMME_CYCLE_VIEW_DETAILS, permissions) ||
    isPermissionDeniedError(error)
  )
    return <PermissionDenied />;

  const { programCycle } = programCycleData;

  const statusChoices: {
    [id: number]: string;
  } = choicesToDict(programChoiceData.programCycleStatusChoices);

  return (
    <Box display='flex' flexDirection='column'>
      <ProgramCycleDetailsHeaderProgramDetails
        programCycle={programCycle}
        permissions={permissions}
      />
      <ProgramCycleDetailsProgramDetails
        programCycle={programCycle}
        statusChoices={statusChoices}
      />

      {hasPermissions(PERMISSIONS.ACTIVITY_LOG_VIEW, permissions) && (
        <UniversalActivityLogTable objectId={programCycle.id} />
      )}
    </Box>
  );
};
