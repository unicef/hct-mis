import { Button } from '@material-ui/core';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useLocation, useParams } from 'react-router-dom';
import styled from 'styled-components';
import {
  PaymentVerificationPlanStatus,
  useCashPlanQuery,
  useCashPlanVerificationSamplingChoicesQuery,
} from '../../../__generated__/graphql';
import { BlackLink } from '../../../components/core/BlackLink';
import { BreadCrumbsItem } from '../../../components/core/BreadCrumbs';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PageHeader } from '../../../components/core/PageHeader';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { TableWrapper } from '../../../components/core/TableWrapper';
import { CashPlanDetailsSection } from '../../../components/payments/CashPlanDetailsSection';
import { CreateVerificationPlan } from '../../../components/payments/CreateVerificationPlan';
import { VerificationPlanDetails } from '../../../components/payments/VerificationPlanDetails';
import { VerificationPlansSummary } from '../../../components/payments/VerificationPlansSummary';
import { PERMISSIONS, hasPermissions } from '../../../config/permissions';
import { useBaseUrl } from '../../../hooks/useBaseUrl';
import { usePermissions } from '../../../hooks/usePermissions';
import {
  decodeIdString,
  getFilterFromQueryParams,
  isPermissionDeniedError,
} from '../../../utils/utils';
import { UniversalActivityLogTablePaymentVerification } from '../../tables/UniversalActivityLogTablePaymentVerification';
import { VerificationRecordsTable } from '../../tables/payments/VerificationRecordsTable';
import { VerificationRecordsFilters } from '../../tables/payments/VerificationRecordsTable/VerificationRecordsFilters';

const Container = styled.div`
  display: flex;
  flex: 1;
  width: 100%;
  background-color: #fff;
  padding: ${({ theme }) => theme.spacing(8)}px
    ${({ theme }) => theme.spacing(11)}px;
  flex-direction: column;
  border-color: #b1b1b5;
  border-bottom-width: 1px;
  border-bottom-style: solid;
`;

const BottomTitle = styled.div`
  color: rgba(0, 0, 0, 0.38);
  font-size: 24px;
  line-height: 28px;
  text-align: center;
  padding: 70px;
`;

const initialFilter = {
  search: '',
  status: '',
  verificationChannel: '',
  paymentVerificationPlan: '',
};

export const CashPlanVerificationDetailsPage = (): React.ReactElement => {
  const { t } = useTranslation();
  const permissions = usePermissions();

  const { baseUrl, businessArea, isAllPrograms } = useBaseUrl();
  const location = useLocation();

  const [filter, setFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const [appliedFilter, setAppliedFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );

  const { id } = useParams();
  const { data, loading, error } = useCashPlanQuery({
    variables: { id },
    fetchPolicy: 'cache-and-network',
  });
  const {
    data: choicesData,
    loading: choicesLoading,
  } = useCashPlanVerificationSamplingChoicesQuery();

  if (loading || choicesLoading) return <LoadingComponent />;

  if (isPermissionDeniedError(error)) return <PermissionDenied />;
  if (!data || !choicesData || permissions === null) return null;

  const { cashPlan } = data;

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: 'Payment Verification',
      to: `/${baseUrl}/payment-verification`,
    },
  ];

  const canCreate = hasPermissions(
    PERMISSIONS.PAYMENT_VERIFICATION_CREATE,
    permissions,
  );

  const statesArray = cashPlan.verificationPlans?.edges?.map(
    (v) => v.node.status,
  );

  const canSeeVerificationRecords = (): boolean => {
    const showTable =
      statesArray.includes(PaymentVerificationPlanStatus.Finished) ||
      statesArray.includes(PaymentVerificationPlanStatus.Active);

    return showTable && statesArray.length > 0;
  };
  const canSeeCreationMessage = (): boolean => {
    return statesArray.length === 0;
  };

  const canSeeActivationMessage = (): boolean => {
    return !canSeeVerificationRecords() && !canSeeCreationMessage();
  };

  const isFinished =
    cashPlan?.paymentVerificationSummary?.status === 'FINISHED';

  const toolbar = (
    <PageHeader
      title={
        <BlackLink fullWidth to={`/${businessArea}/cashplans/${cashPlan.id}`}>
          {t('Payment Plan')} {cashPlan.caId}
        </BlackLink>
      }
      breadCrumbs={
        hasPermissions(PERMISSIONS.PAYMENT_VERIFICATION_VIEW_LIST, permissions)
          ? breadCrumbsItems
          : null
      }
    >
      <>
        {canCreate && (
          <CreateVerificationPlan
            disabled={false}
            cashOrPaymentPlanId={cashPlan.id}
            canCreatePaymentVerificationPlan={
              cashPlan.canCreatePaymentVerificationPlan
            }
          />
        )}

        {isFinished &&
          (isAllPrograms ? (
            <Button
              variant='contained'
              color='primary'
              component={Link}
              to={`/${baseUrl}/grievance/payment-verification/${decodeIdString(
                cashPlan.id,
              )}`}
            >
              {t('View Tickets')}
            </Button>
          ) : null)}
      </>
    </PageHeader>
  );

  return (
    <>
      {toolbar}
      <Container>
        <CashPlanDetailsSection planNode={cashPlan} />
      </Container>
      <Container>
        <VerificationPlansSummary planNode={cashPlan} />
      </Container>
      {cashPlan.verificationPlans?.edges?.length
        ? cashPlan.verificationPlans.edges.map((edge) => (
            <VerificationPlanDetails
              key={edge.node.id}
              samplingChoicesData={choicesData}
              verificationPlan={edge.node}
              planNode={cashPlan}
            />
          ))
        : null}
      {canSeeVerificationRecords() ? (
        <>
          <Container>
            <VerificationRecordsFilters
              filter={filter}
              setFilter={setFilter}
              initialFilter={initialFilter}
              appliedFilter={appliedFilter}
              setAppliedFilter={setAppliedFilter}
              verifications={cashPlan.verificationPlans}
            />
          </Container>
          <TableWrapper>
            <VerificationRecordsTable
              paymentPlanId={cashPlan.id}
              filter={appliedFilter}
              businessArea={businessArea}
              canViewRecordDetails={hasPermissions(
                PERMISSIONS.PAYMENT_VERIFICATION_VIEW_PAYMENT_RECORD_DETAILS,
                permissions,
              )}
            />
          </TableWrapper>
        </>
      ) : null}
      {canSeeActivationMessage() ? (
        <BottomTitle>
          {t('To see more details please activate Verification Plan')}
        </BottomTitle>
      ) : null}

      {canSeeCreationMessage() ? (
        <BottomTitle>
          {t('To see more details please create Verification Plan')}
        </BottomTitle>
      ) : null}
      {cashPlan.verificationPlans?.edges[0]?.node?.id &&
        hasPermissions(PERMISSIONS.ACTIVITY_LOG_VIEW, permissions) && (
          <UniversalActivityLogTablePaymentVerification
            objectId={cashPlan.id}
          />
        )}
    </>
  );
};
