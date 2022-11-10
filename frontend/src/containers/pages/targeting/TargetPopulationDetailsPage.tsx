import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import {
  TargetPopulationBuildStatus,
  TargetPopulationStatus,
  useTargetPopulationQuery,
} from '../../../__generated__/graphql';
import { EditTargetPopulation } from '../../../components/targeting/EditTargetPopulation/EditTargetPopulation';
import { TargetPopulationCore } from '../../../components/targeting/TargetPopulationCore';
import { TargetPopulationDetails } from '../../../components/targeting/TargetPopulationDetails';
import { usePermissions } from '../../../hooks/usePermissions';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { isPermissionDeniedError } from '../../../utils/utils';
import { TargetPopulationPageHeader } from '../headers/TargetPopulationPageHeader';
import { useLazyInterval } from '../../../hooks/useInterval';

export const TargetPopulationDetailsPage = (): React.ReactElement => {
  const { id } = useParams();
  const permissions = usePermissions();
  const { data, loading, error, refetch } = useTargetPopulationQuery({
    variables: { id },
    fetchPolicy: 'cache-and-network',
  });
  const [
    startPollingTargetPopulation,
    stopPollingTargetPopulation,
  ] = useLazyInterval(() => refetch(), 3000);
  const buildStatus = data?.targetPopulation?.buildStatus;
  useEffect(() => {
    if (buildStatus !== TargetPopulationBuildStatus.Ok) {
      startPollingTargetPopulation();
    } else {
      stopPollingTargetPopulation();
    }
    return stopPollingTargetPopulation;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [buildStatus]);
  const [isEdit, setEditState] = useState(false);

  if (loading && !data) return <LoadingComponent />;

  if (isPermissionDeniedError(error)) return <PermissionDenied />;

  if (!data || permissions === null) return null;

  const { targetPopulation } = data;
  const { status } = targetPopulation;

  const canDuplicate =
    hasPermissions(PERMISSIONS.TARGETING_DUPLICATE, permissions) &&
    Boolean(targetPopulation.targetingCriteria);

  return (
    <>
      {isEdit ? (
        <EditTargetPopulation
          targetPopulation={targetPopulation}
          cancelEdit={() => setEditState(false)}
        />
      ) : (
        <>
          <TargetPopulationPageHeader
            targetPopulation={targetPopulation}
            setEditState={setEditState}
            canEdit={hasPermissions(PERMISSIONS.TARGETING_UPDATE, permissions)}
            canRemove={hasPermissions(
              PERMISSIONS.TARGETING_REMOVE,
              permissions,
            )}
            canDuplicate={canDuplicate}
            canLock={hasPermissions(PERMISSIONS.TARGETING_LOCK, permissions)}
            canUnlock={hasPermissions(
              PERMISSIONS.TARGETING_UNLOCK,
              permissions,
            )}
            canSend={hasPermissions(PERMISSIONS.TARGETING_SEND, permissions)}
          />
          {status !== TargetPopulationStatus.Open && (
            <TargetPopulationDetails targetPopulation={targetPopulation} />
          )}
          <TargetPopulationCore
            id={targetPopulation.id}
            targetPopulation={targetPopulation}
            permissions={permissions}
          />
        </>
      )}
    </>
  );
};
