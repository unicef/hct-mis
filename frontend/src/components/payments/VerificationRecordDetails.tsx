import React from 'react';
import styled from 'styled-components';
import moment from 'moment';
import { Grid, Paper, Typography } from '@material-ui/core';
import { StatusBox } from '../StatusBox';
import { decodeIdString, paymentRecordStatusToColor } from '../../utils/utils';
import { LabelizedField } from '../LabelizedField';
import { PaymentVerificationNode } from '../../__generated__/graphql';
import { Missing } from '../Missing';

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
const OverviewContainer = styled.div`
  display: flex;
  align-items: center;
  flex-direction: row;
`;

const StatusContainer = styled.div`
  width: 120px;
`;

const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

const OverviewGrid = styled(Grid)`
  max-width: 1000px;
`;
const PageContainer = styled.div`
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  padding: ${({ theme }) => theme.spacing(5)}px;
`;

const Card = styled(Paper)`
  padding: ${({ theme }) => theme.spacing(6)}px;
`;

const HouseholdDataContainer = styled.div`
  margin-top: ${({ theme }) => theme.spacing(2)}px;
`;
const LabelizedFieldContainer = styled.div`
  margin-top: ${({ theme }) => theme.spacing(6)}px;
`;
const EntitlementDataContainer = styled.div`
  margin-top: ${({ theme }) => theme.spacing(6)}px;
`;

interface VerificationRecordDetailsProps {
  paymentVerification: PaymentVerificationNode;
}

export function VerificationRecordDetails({
  paymentVerification,
}: VerificationRecordDetailsProps): React.ReactElement {
  return (
    <>
      <Container>
        <Title>
          <Typography variant='h6'>Payment Record Details</Typography>
        </Title>
        <OverviewContainer>
          <OverviewGrid container spacing={6}>
            <Grid item xs={4}>
              <LabelizedField label='status'>
                <StatusContainer>
                  <StatusBox
                    status={paymentVerification.status}
                    statusToColor={paymentRecordStatusToColor}
                  />
                </StatusContainer>
              </LabelizedField>
            </Grid>

            <Grid item xs={4}>
              <LabelizedField
                label='Status date'
                value={moment(paymentVerification.statusDate).format(
                  'DD MMM YYYY',
                )}
              />
            </Grid>
            <Grid item xs={4}>
              <LabelizedField
                label='Distribution Modality'
                value={paymentVerification.paymentRecord.distributionModality}
              />
            </Grid>
            <Grid item xs={4}>
              <LabelizedField
                label='Target Population'
                value={paymentVerification.paymentRecord.targetPopulation.name}
              />
            </Grid>
          </OverviewGrid>
        </OverviewContainer>
      </Container>

      <PageContainer>
        <Grid container spacing={5}>
          <Grid item xs={4}>
            <Card>
              <Typography variant='h6'>Household</Typography>
              <HouseholdDataContainer>
                <LabelizedFieldContainer>
                  <LabelizedField
                    label='household id'
                    value={decodeIdString(
                      paymentVerification.paymentRecord.household.id,
                    )}
                  />
                </LabelizedFieldContainer>
                <LabelizedFieldContainer>
                  <LabelizedField
                    label='head of household'
                    value={paymentVerification.paymentRecord.fullName}
                  />
                </LabelizedFieldContainer>
                <LabelizedFieldContainer>
                  <LabelizedField
                    label='total person covered'
                    value={
                      paymentVerification.paymentRecord.totalPersonsCovered
                    }
                  />
                </LabelizedFieldContainer>
              </HouseholdDataContainer>
            </Card>
          </Grid>

          <Grid item xs={8}>
            <Card>
              <Typography variant='h6'>Entitlement Details</Typography>
              <EntitlementDataContainer>
                <Grid container spacing={6}>
                  <Grid item xs={4}>
                    <LabelizedField
                      label='Entitlement quantity'
                      value={
                        paymentVerification.paymentRecord.entitlementQuantity
                      }
                    />
                  </Grid>
                  <Grid item xs={4}>
                    <LabelizedField
                      label='Currency'
                      value={paymentVerification.paymentRecord.currency}
                    />
                  </Grid>
                  <Grid item xs={4}>
                    <LabelizedField
                      label='Delivery type'
                      value={paymentVerification.paymentRecord.deliveryType}
                    />
                  </Grid>

                  <Grid item xs={4}>
                    <LabelizedField
                      label='Delivered quantity'
                      value={
                        paymentVerification.paymentRecord.deliveredQuantity
                      }
                    />
                  </Grid>
                  <Grid item xs={4}>
                    <LabelizedField
                      label='Delivery date'
                      value={moment(
                        paymentVerification.paymentRecord.deliveryDate,
                      ).format('DD MMM YYYY')}
                    />
                  </Grid>
                  <Grid item xs={4}>
                    <Missing />
                  </Grid>

                  <Grid item xs={4}>
                    <LabelizedField
                      label='Entitlement Card Number'
                      value={
                        paymentVerification.paymentRecord.entitlementCardNumber
                      }
                    />
                  </Grid>
                  <Grid item xs={4}>
                    <LabelizedField
                      label='Entitlement Card Issue Date'
                      value={moment(
                        paymentVerification.paymentRecord
                          .entitlementCardIssueDate,
                      ).format('DD MMM YYYY')}
                    />
                  </Grid>
                  <Grid item xs={4}>
                    <LabelizedField
                      label='FSP'
                      value={
                        paymentVerification.paymentRecord.serviceProvider
                          .fullName
                      }
                    />
                  </Grid>
                </Grid>
              </EntitlementDataContainer>
            </Card>
          </Grid>
        </Grid>
      </PageContainer>
    </>
  );
}
