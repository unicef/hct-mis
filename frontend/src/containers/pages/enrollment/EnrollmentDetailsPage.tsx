import React, { useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { TargetPopulationCore } from '../../../components/targeting/TargetPopulationCore';
import { TargetPopulationDetails } from '../../../components/targeting/TargetPopulationDetails';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { usePermissions } from '../../../hooks/usePermissions';
import { isPermissionDeniedError } from '../../../utils/utils';
import {
  TargetPopulationBuildStatus,
  useTargetPopulationQuery,
} from '../../../__generated__/graphql';
import { TargetPopulationPageHeader } from '../headers/TargetPopulationPageHeader';

export const EnrollmentDetailsPage = (): React.ReactElement => {
  const { id } = useParams();
  const permissions = usePermissions();
  const {
    data,
    loading,
    error,
    startPolling,
    stopPolling,
  } = useTargetPopulationQuery({
    variables: { id },
    fetchPolicy: 'cache-and-network',
  });

  const buildStatus = data?.targetPopulation?.buildStatus;
  useEffect(() => {
    if (
      [
        TargetPopulationBuildStatus.Building,
        TargetPopulationBuildStatus.Pending,
      ].includes(buildStatus)
    ) {
      startPolling(3000);
    } else {
      stopPolling();
    }
    return stopPolling;
  }, [buildStatus, startPolling, stopPolling]);

  if (loading && !data) return <LoadingComponent />;

  if (isPermissionDeniedError(error)) return <PermissionDenied />;

  if (!data || permissions === null) return null;

  const { targetPopulation } = data;

  const canDuplicate =
    hasPermissions(PERMISSIONS.TARGETING_DUPLICATE, permissions) &&
    Boolean(targetPopulation.targetingCriteria);

  return (
    <>
      <EnrollmentPageHeader
        targetPopulation={targetPopulation}
        canEdit={hasPermissions(PERMISSIONS.TARGETING_UPDATE, permissions)}
        canRemove={hasPermissions(PERMISSIONS.TARGETING_REMOVE, permissions)}
        canDuplicate={canDuplicate}
        canLock={hasPermissions(PERMISSIONS.TARGETING_LOCK, permissions)}
        canUnlock={hasPermissions(PERMISSIONS.TARGETING_UNLOCK, permissions)}
        canSend={hasPermissions(PERMISSIONS.TARGETING_SEND, permissions)}
      />
      <EnrollmentDetails targetPopulation={targetPopulation} />
      <EnrollmentCore
        id={targetPopulation.id}
        targetPopulation={targetPopulation}
        permissions={permissions}
      />
    </>
  );
};
