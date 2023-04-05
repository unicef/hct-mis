import React, { useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { AcceptanceProcess } from '../../../components/paymentmodule/PaymentPlanDetails/AcceptanceProcess/AcceptanceProcess';
import { Entitlement } from '../../../components/paymentmodule/PaymentPlanDetails/Entitlement/Entitlement';
import { FspSection } from '../../../components/paymentmodule/PaymentPlanDetails/FspSection';
import { PaymentPlanDetails } from '../../../components/paymentmodule/PaymentPlanDetails/PaymentPlanDetails';
import { PaymentPlanDetailsHeader } from '../../../components/paymentmodule/PaymentPlanDetails/PaymentPlanDetailsHeader';
import { PaymentPlanDetailsResults } from '../../../components/paymentmodule/PaymentPlanDetails/PaymentPlanDetailsResults';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { usePermissions } from '../../../hooks/usePermissions';
import { PaymentsTable } from '../../tables/paymentmodule/PaymentsTable';
import {
  PaymentPlanStatus,
  usePaymentPlanQuery,
} from '../../../__generated__/graphql';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { UniversalActivityLogTable } from '../../tables/UniversalActivityLogTable';
import { ReconciliationSummary } from '../../../components/paymentmodule/PaymentPlanDetails/ReconciliationSummary';

export const PaymentPlanDetailsPage = (): React.ReactElement => {
  const { id } = useParams();
  const permissions = usePermissions();
  const businessArea = useBusinessArea();
  const { data, loading, startPolling, stopPolling } = usePaymentPlanQuery({
    variables: {
      id,
    },
    fetchPolicy: 'cache-and-network',
  });

  const status = data?.paymentPlan?.status;

  useEffect(() => {
    if (PaymentPlanStatus.Preparing === status) {
      startPolling(3000);
    } else {
      stopPolling();
    }
    return stopPolling;
  }, [status, startPolling, stopPolling]);

  if (loading && !data) return <LoadingComponent />;
  if (permissions === null || !data) return null;

  if (!hasPermissions(PERMISSIONS.PM_VIEW_DETAILS, permissions))
    return <PermissionDenied />;

  const shouldDisplayEntitlement =
    status !== PaymentPlanStatus.Open && status !== PaymentPlanStatus.Accepted;

  const shouldDisplayFsp = status !== PaymentPlanStatus.Open;
  const shouldDisplayReconciliationSummary =
    status === PaymentPlanStatus.Accepted ||
    status === PaymentPlanStatus.Finished;

  const { paymentPlan } = data;
  return (
    <>
      <PaymentPlanDetailsHeader
        paymentPlan={paymentPlan}
        businessArea={businessArea}
        permissions={permissions}
      />
      <PaymentPlanDetails
        businessArea={businessArea}
        paymentPlan={paymentPlan}
      />
      <AcceptanceProcess paymentPlan={paymentPlan} />
      {shouldDisplayEntitlement && (
        <Entitlement paymentPlan={paymentPlan} permissions={permissions} />
      )}
      {shouldDisplayFsp && (
        <FspSection businessArea={businessArea} paymentPlan={paymentPlan} />
      )}
      <PaymentPlanDetailsResults paymentPlan={paymentPlan} />
      <PaymentsTable
        businessArea={businessArea}
        paymentPlan={paymentPlan}
        permissions={permissions}
        canViewDetails
      />
      {shouldDisplayReconciliationSummary && (
        <ReconciliationSummary paymentPlan={paymentPlan} />
      )}
      {hasPermissions(PERMISSIONS.ACTIVITY_LOG_VIEW, permissions) && (
        <UniversalActivityLogTable objectId={paymentPlan.id} />
      )}
    </>
  );
};
