import React from 'react';
import { useParams } from 'react-router-dom';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { SetUpFspCore } from '../../../components/paymentmodule/CreateSetUpFsp/SetUpFspCore/SetUpFspCore';
import { EditSetUpFspHeader } from '../../../components/paymentmodule/EditSetUpFsp/EditSetUpFspHeader';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { usePermissions } from '../../../hooks/usePermissions';
import { usePaymentPlanQuery } from '../../../__generated__/graphql';

export const EditSetUpFspPage = (): React.ReactElement => {
  const { id } = useParams();

  const {
    data: paymentPlanData,
    loading: paymentPlanLoading,
  } = usePaymentPlanQuery({
    variables: {
      id,
    },
    fetchPolicy: 'cache-and-network',
  });

  const businessArea = useBusinessArea();
  const permissions = usePermissions();

  if (permissions === null) return null;
  if (
    !hasPermissions(
      PERMISSIONS.PM_LOCK_AND_UNLOCK_FSP,
      permissions,
    )
  )
    return <PermissionDenied />;
  if (!paymentPlanData) return null;
  if (paymentPlanLoading) return <LoadingComponent />;

  const mappedInitialDeliveryMechanisms = paymentPlanData.paymentPlan.deliveryMechanisms.map(
    (el) => ({
      deliveryMechanism: el.name,
      fsp: el.fsp?.id || '',
    }),
  );

  const initialValues = {
    deliveryMechanisms: mappedInitialDeliveryMechanisms,
  };

  return (
    <>
      <EditSetUpFspHeader
        businessArea={businessArea}
        permissions={permissions}
      />
      <SetUpFspCore
        businessArea={businessArea}
        permissions={permissions}
        initialValues={initialValues}
      />
    </>
  );
};
