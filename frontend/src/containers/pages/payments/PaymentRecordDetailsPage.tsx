import { Button } from '@material-ui/core';
import OpenInNewRoundedIcon from '@material-ui/icons/OpenInNewRounded';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import { BreadCrumbsItem } from '../../../components/core/BreadCrumbs';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PageHeader } from '../../../components/core/PageHeader';
import { PaymentRecordDetails } from '../../../components/payments/PaymentRecordDetails';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { usePermissions } from '../../../hooks/usePermissions';
import {
  PaymentRecordNode,
  useCashAssistUrlPrefixQuery,
  usePaymentRecordQuery,
} from '../../../__generated__/graphql';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  width: 100%;
`;
const ButtonContainer = styled.span`
  margin: 0 ${({ theme }) => theme.spacing(2)}px;
`;

export function PaymentRecordDetailsPage(): React.ReactElement {
  const { t } = useTranslation();
  const { id } = useParams();
  const { data: caData, loading: caLoading } = useCashAssistUrlPrefixQuery({fetchPolicy:"cache-first"});
  const { data, loading } = usePaymentRecordQuery({
    variables: { id },
    fetchPolicy: 'cache-and-network',
  });
  const permissions = usePermissions();
  const businessArea = useBusinessArea();
  if (loading || caLoading) return <LoadingComponent />;
  if (permissions === null) return null;
  if (
    !hasPermissions(
      PERMISSIONS.PROGRAMME_VIEW_PAYMENT_RECORD_DETAILS,
      permissions,
    )
  )
    return <PermissionDenied />;

  if (!data || !caData) return null;

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Programme Management'),
      to: `/${businessArea}/programs/`,
    },
    {
      title: data.paymentRecord.cashPlan.program.name,
      to: `/${businessArea}/programs/${data.paymentRecord.cashPlan.program.id}/`,
    },
    {
      title: `Cash Plan #${data.paymentRecord.cashPlan.caId}`,
      to: `/${businessArea}/cashplans/${data.paymentRecord.cashPlan.id}`,
    },
  ];
  const paymentRecord = data.paymentRecord as PaymentRecordNode;
  return (
    <div>
      <PageHeader
        title={`Payment ID ${paymentRecord.caId}`}
        breadCrumbs={breadCrumbsItems}
      >
        <ButtonContainer>
          <Button
            variant='contained'
            color='primary'
            component='a'
            disabled={!paymentRecord.caHashId || !caData?.cashAssistUrlPrefix}
            target='_blank'
            href={`${caData?.cashAssistUrlPrefix}&pagetype=entityrecord&etn=progres_payment&id=${paymentRecord.caHashId}`}
            startIcon={<OpenInNewRoundedIcon />}
          >
            {t('Open in CashAssist')}
          </Button>
        </ButtonContainer>
      </PageHeader>
      <Container>
        <PaymentRecordDetails
          paymentRecord={paymentRecord}
          canViewActivityLog={hasPermissions(
            PERMISSIONS.ACTIVITY_LOG_VIEW,
            permissions,
          )}
        />
      </Container>
    </div>
  );
}
