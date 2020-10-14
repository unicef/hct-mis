import React, { useState } from 'react';
import styled from 'styled-components';
import { Box, Grid, Typography } from '@material-ui/core';
import { Doughnut } from 'react-chartjs-2';
import { useParams } from 'react-router-dom';
import { PageHeader } from '../../components/PageHeader';
import { LabelizedField } from '../../components/LabelizedField';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { BreadCrumbsItem } from '../../components/BreadCrumbs';
import { UniversalActivityLogTable } from '../tables/UniversalActivityLogTable';
import { EditVerificationPlan } from '../../components/payments/EditVerificationPlan';
import { ActivateVerificationPlan } from '../../components/payments/ActivateVerificationPlan';
import { FinishVerificationPlan } from '../../components/payments/FinishVerificationPlan';
import { DiscardVerificationPlan } from '../../components/payments/DiscardVerificationPlan';
import {
  useCashPlanQuery,
  useCashPlanVerificationSamplingChoicesQuery,
} from '../../__generated__/graphql';
import { LoadingComponent } from '../../components/LoadingComponent';
import {
  choicesToDict,
  decodeIdString,
  paymentVerificationStatusToColor,
} from '../../utils/utils';
import { StatusBox } from '../../components/StatusBox';
import { VerificationRecordsTable } from '../tables/VerificationRecordsTable';
import { useDebounce } from '../../hooks/useDebounce';
import { VerificationRecordsFilters } from '../tables/VerificationRecordsTable/VerificationRecordsFilters';
import { CreateVerificationPlan } from '../../components/payments/CreateVerificationPlan';
import { UniversalMoment } from '../../components/UniversalMoment';
import { usePermissions } from '../../hooks/usePermissions';
import { hasPermissions, PERMISSIONS } from '../../config/permissions';

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

const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

const ChartContainer = styled.div`
  width: 100px;
  height: 100px;
`;

const BorderLeftBox = styled.div`
  padding-left: ${({ theme }) => theme.spacing(6)}px;
  border-left: 1px solid #e0e0e0;
  height: 100%;
`;

const BottomTitle = styled.div`
  color: rgba(0, 0, 0, 0.38);
  font-size: 24px;
  line-height: 28px;
  text-align: center;
  padding: 70px;
`;

const TableWrapper = styled.div`
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  padding: 20px;
  padding-bottom: 0;
`;
const StatusContainer = styled.div`
  min-width: 120px;
  max-width: 200px;
`;

export function PaymentVerificationDetailsPage(): React.ReactElement {
  const permissions = usePermissions();
  const businessArea = useBusinessArea();
  const [filter, setFilter] = useState({
    search: null,
  });
  const debouncedFilter = useDebounce(filter, 500);
  const { id } = useParams();
  const { data, loading } = useCashPlanQuery({
    variables: { id },
  });
  const {
    data: choicesData,
    loading: choicesLoading,
  } = useCashPlanVerificationSamplingChoicesQuery();
  if (!data || choicesLoading || permissions === null) return null;

  if (loading) {
    return <LoadingComponent />;
  }

  const samplingChoicesDict = choicesToDict(
    choicesData.cashPlanVerificationSamplingChoices,
  );
  const { cashPlan } = data;
  const verificationPlan = cashPlan?.verifications?.edges?.length
    ? cashPlan.verifications.edges[0].node
    : null;
  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: 'Payment Verification',
      to: `/${businessArea}/payment-verification/`,
    },
  ];
  const bankReconciliationSuccessPercentage =
    (cashPlan.bankReconciliationSuccess / cashPlan.paymentRecords.totalCount) *
    100;
  const bankReconciliationErrorPercentage =
    (cashPlan.bankReconciliationError / cashPlan.paymentRecords.totalCount) *
    100;

  const canCreate =
    cashPlan.verificationStatus === 'PENDING' &&
    cashPlan.verifications &&
    cashPlan.verifications.edges.length === 0;

  const canEditAndActivate =
    cashPlan.verificationStatus === 'PENDING' &&
    cashPlan.verifications &&
    cashPlan.verifications.edges.length !== 0;

  const canFinishAndDiscard =
    cashPlan.verificationStatus === 'ACTIVE' &&
    cashPlan.verifications &&
    cashPlan.verifications.edges.length !== 0;

  const toolbar = (
    <PageHeader
      title={`Cash Plan ${decodeIdString(cashPlan.id)}`}
      breadCrumbs={breadCrumbsItems}
    >
      <>
        {canCreate && (
          <CreateVerificationPlan disabled={false} cashPlanId={cashPlan.id} />
        )}
        {canEditAndActivate && (
          <Box alignItems='center' display='flex'>
            <EditVerificationPlan
              cashPlanId={cashPlan.id}
              cashPlanVerificationId={cashPlan.verifications.edges[0].node.id}
            />
            <ActivateVerificationPlan
              cashPlanId={cashPlan.id}
              cashPlanVerificationId={cashPlan.verifications.edges[0].node.id}
            />
          </Box>
        )}
        {canFinishAndDiscard && (
          <Box display='flex'>
            <FinishVerificationPlan
              cashPlanId={cashPlan.id}
              cashPlanVerificationId={cashPlan.verifications.edges[0].node.id}
            />
            <DiscardVerificationPlan
              cashPlanId={cashPlan.id}
              cashPlanVerificationId={cashPlan.verifications.edges[0].node.id}
            />
          </Box>
        )}
      </>
    </PageHeader>
  );

  return (
    <>
      {toolbar}
      <Container>
        <Grid container>
          <Grid item xs={9}>
            <Title>
              <Typography variant='h6'>Cash Plan Details</Typography>
            </Title>
            <Grid container>
              {[
                { label: 'PROGRAMME NAME', value: cashPlan.program.name },
                {
                  label: 'PROGRAMME ID',
                  value: decodeIdString(cashPlan.program.id),
                },
                {
                  label: 'PAYMENT RECORDS',
                  value: cashPlan.paymentRecords.totalCount,
                },
                {
                  label: 'START DATE',
                  value: (
                    <UniversalMoment>{cashPlan.startDate}</UniversalMoment>
                  ),
                },
                {
                  label: 'END DATE',
                  value: <UniversalMoment>{cashPlan.endDate}</UniversalMoment>,
                },
              ].map((el) => (
                <Grid item xs={4}>
                  <LabelizedField label={el.label}>
                    <p>{el.value}</p>
                  </LabelizedField>
                </Grid>
              ))}
            </Grid>
          </Grid>
          <Grid item xs={3}>
            <BorderLeftBox>
              <Title>
                <Typography variant='h6'>Bank reconciliation</Typography>
              </Title>
              <Grid container>
                <Grid item xs={6}>
                  <Grid container direction='column'>
                    <LabelizedField label='SUCCESSFUL'>
                      <p>{bankReconciliationSuccessPercentage.toFixed(2)}%</p>
                    </LabelizedField>
                    <LabelizedField label='ERRONEUS'>
                      <p>{bankReconciliationErrorPercentage.toFixed(2)}%</p>
                    </LabelizedField>
                  </Grid>
                </Grid>
                <Grid item xs={6}>
                  <ChartContainer>
                    <Doughnut
                      width={100}
                      height={100}
                      options={{
                        maintainAspectRatio: false,
                        cutoutPercentage: 65,
                        legend: {
                          display: false,
                        },
                      }}
                      data={{
                        labels: ['Successful', 'Erroneus'],
                        datasets: [
                          {
                            data: [
                              bankReconciliationSuccessPercentage,
                              bankReconciliationErrorPercentage,
                            ],
                            backgroundColor: ['#00509F', '#FFAA1F'],
                            hoverBackgroundColor: ['#00509F', '#FFAA1F'],
                          },
                        ],
                      }}
                    />
                  </ChartContainer>
                </Grid>
              </Grid>
            </BorderLeftBox>
          </Grid>
        </Grid>
      </Container>
      {cashPlan.verifications && cashPlan.verifications.edges.length ? (
        <Container>
          <Title>
            <Typography variant='h6'>Verification Plan Details</Typography>
          </Title>
          <Grid container>
            <Grid item xs={11}>
              <Grid container>
                <Grid item xs={3}>
                  <LabelizedField label='STATUS'>
                    <StatusContainer>
                      <StatusBox
                        status={verificationPlan.status}
                        statusToColor={paymentVerificationStatusToColor}
                      />
                    </StatusContainer>
                  </LabelizedField>
                </Grid>
                {[
                  {
                    label: 'SAMPLING',
                    value: samplingChoicesDict[verificationPlan.sampling],
                  },
                  {
                    label: 'RESPONDED',
                    value: verificationPlan.respondedCount || '-',
                  },
                  {
                    label: 'RECEIVED WITH ISSUES',
                    value: verificationPlan.receivedWithProblemsCount || '-',
                  },
                  {
                    label: 'VERIFICATION METHOD',
                    value: verificationPlan.verificationMethod,
                  },
                  { label: 'SAMPLE SIZE', value: verificationPlan.sampleSize },
                  {
                    label: 'RECEIVED',
                    value: verificationPlan.receivedCount || '-',
                  },
                  {
                    label: 'NOT RECEIVED',
                    value: verificationPlan.notReceivedCount || '-',
                  },
                  {
                    label: 'ACTIVATION DATE',
                    value: (
                      <UniversalMoment>
                        {verificationPlan.activationDate}
                      </UniversalMoment>
                    ),
                  },
                  {
                    label: 'COMPLETION DATE',
                    value: (
                      <UniversalMoment>
                        {verificationPlan.completionDate}
                      </UniversalMoment>
                    ),
                  },
                ].map((el) => (
                  <Grid item xs={3}>
                    <LabelizedField label={el.label}>
                      <p>{el.value}</p>
                    </LabelizedField>
                  </Grid>
                ))}
              </Grid>
            </Grid>
            <Grid item xs={1}>
              <ChartContainer>
                <Doughnut
                  width={200}
                  height={200}
                  options={{
                    maintainAspectRatio: false,
                    cutoutPercentage: 65,
                    legend: {
                      display: false,
                    },
                  }}
                  data={{
                    labels: [
                      'RECEIVED',
                      'RECEIVED WITH ISSUES',
                      'NOT RECEIVED',
                      'PENDING',
                    ],
                    datasets: [
                      {
                        data: [
                          verificationPlan.receivedCount,
                          verificationPlan.receivedWithProblemsCount,
                          verificationPlan.notReceivedCount,
                          verificationPlan.sampleSize -
                            verificationPlan.respondedCount,
                        ],
                        backgroundColor: [
                          '#31D237',
                          '#F57F1A',
                          '#FF0100',
                          '#DCDCDC',
                        ],
                        hoverBackgroundColor: [
                          '#31D237',
                          '#F57F1A',
                          '#FF0100',
                          '#DCDCDC',
                        ],
                      },
                    ],
                  }}
                />
              </ChartContainer>
            </Grid>
          </Grid>
        </Container>
      ) : null}
      {cashPlan.verifications &&
      cashPlan.verifications.edges.length &&
      cashPlan.verificationStatus === 'ACTIVE' ? (
        <>
          <Container>
            <VerificationRecordsFilters
              filter={filter}
              onFilterChange={setFilter}
            />
          </Container>
          <Container>
            <VerificationRecordsTable
              verificationMethod={verificationPlan.verificationMethod}
              filter={debouncedFilter}
              id={verificationPlan.id}
            />
          </Container>
        </>
      ) : null}
      {cashPlan.verifications &&
      cashPlan.verifications.edges.length &&
      cashPlan.verificationStatus !== 'ACTIVE' &&
      cashPlan.verificationStatus !== 'FINISHED' ? (
        <BottomTitle>
          To see more details please activate Verification Plan
        </BottomTitle>
      ) : null}
      {!cashPlan.verifications.edges.length &&
      cashPlan.verificationStatus !== 'ACTIVE' ? (
        <BottomTitle>
          To see more details please create Verification Plan
        </BottomTitle>
      ) : null}
      {cashPlan.verificationStatus === 'TRANSACTION_COMPLETED_WITH_ERRORS' ? (
        <BottomTitle>Transaction completed with errors</BottomTitle>
      ) : null}
      {cashPlan.verifications?.edges[0]?.node?.id && (
        <TableWrapper>
          <UniversalActivityLogTable
            objectId={cashPlan.verifications.edges[0].node.id}
          />
        </TableWrapper>
      )}
    </>
  );
}
