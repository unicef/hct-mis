import React from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
<<<<<<< HEAD
import { BreadCrumbsItem } from '../../../components/core/BreadCrumbs';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PageHeader } from '../../../components/core/PageHeader';
import { VerificationPaymentRecordDetails } from '../../../components/payments/VerificationPaymentRecordDetails';
import { VerifyManual } from '../../../components/payments/VerifyManual';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { usePermissions } from '../../../hooks/usePermissions';
import { decodeIdString, isPermissionDeniedError } from '../../../utils/utils';
=======
>>>>>>> develop
import {
  usePaymentRecordQuery,
  usePaymentVerificationChoicesQuery,
} from '../../../__generated__/graphql';
<<<<<<< HEAD
import { useBaseUrl } from '../../../hooks/useBaseUrl';
=======
import { BreadCrumbsItem } from '../../../components/core/BreadCrumbs';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PageHeader } from '../../../components/core/PageHeader';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { VerificationPaymentRecordDetails } from '../../../components/payments/VerificationPaymentRecordDetails';
import { VerifyManual } from '../../../components/payments/VerifyManual';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { usePermissions } from '../../../hooks/usePermissions';
import { isPermissionDeniedError } from '../../../utils/utils';
>>>>>>> develop

export function VerificationPaymentRecordDetailsPage(): React.ReactElement {
  const { t } = useTranslation();
  const { id } = useParams();
  const permissions = usePermissions();
  const { data, loading, error } = usePaymentRecordQuery({
    variables: { id },
    fetchPolicy: 'cache-and-network',
  });
  const {
    data: choicesData,
    loading: choicesLoading,
  } = usePaymentVerificationChoicesQuery();
  const { baseUrl } = useBaseUrl();
  if (loading || choicesLoading) return <LoadingComponent />;
  if (isPermissionDeniedError(error)) return <PermissionDenied />;
  const { paymentRecord } = data;
  if (!paymentRecord || !choicesData || permissions === null) return null;

  const verification = paymentRecord.parent?.verificationPlans?.edges[0].node;
  const breadCrumbsItems: BreadCrumbsItem[] = [
    ...(hasPermissions(PERMISSIONS.PAYMENT_VERIFICATION_VIEW_LIST, permissions)
      ? [
          {
            title: t('Payment Verification'),
            to: `/${baseUrl}/payment-verification`,
          },
        ]
      : []),
    ...(hasPermissions(
      PERMISSIONS.PAYMENT_VERIFICATION_VIEW_DETAILS,
      permissions,
    )
      ? [
          {
<<<<<<< HEAD
            title: `${t('Payment Plan')} ${decodeIdString(
              paymentRecord.parent.id,
            )}`,
            to: `/${baseUrl}/payment-verification/cash-plan/${paymentRecord.parent.id}`,
=======
            title: `${t('Payment Plan')} ${paymentRecord.parent.unicefId}`,
            to: `/${businessArea}/payment-verification/cash-plan/${paymentRecord.parent.id}`,
>>>>>>> develop
          },
        ]
      : []),
  ];

  const toolbar = (
    <PageHeader
      title={`${t('Payment Record ID')} ${paymentRecord.caId}`}
      breadCrumbs={breadCrumbsItems}
    >
      {verification.verificationChannel === 'MANUAL' &&
      hasPermissions(PERMISSIONS.PAYMENT_VERIFICATION_VERIFY, permissions) ? (
        <VerifyManual
          paymentVerificationId={paymentRecord.verification.id}
          enabled={paymentRecord.verification.isManuallyEditable}
        />
      ) : null}
    </PageHeader>
  );
  return (
    <div>
      {toolbar}
      <VerificationPaymentRecordDetails
        paymentRecord={paymentRecord}
        canViewActivityLog={hasPermissions(
          PERMISSIONS.ACTIVITY_LOG_VIEW,
          permissions,
        )}
        choicesData={choicesData}
      />
    </div>
  );
}
