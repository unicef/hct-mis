import React from 'react';
import styled from 'styled-components';
import { Grid, Paper, Typography } from '@material-ui/core';
import { StatusBox } from '../StatusBox';
import {
  formatCurrency,
  paymentRecordStatusToColor,
  verificationRecordsStatusToColor,
} from '../../utils/utils';
import { LabelizedField } from '../LabelizedField';
import { PaymentVerificationNode } from '../../__generated__/graphql';
import { UniversalActivityLogTable } from '../../containers/tables/UniversalActivityLogTable';
import { UniversalMoment } from '../UniversalMoment';
import { ContainerColumnWithBorder } from '../ContainerColumnWithBorder';

const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

const Overview = styled(Paper)`
  margin: 20px;
  padding: ${({ theme }) => theme.spacing(8)}px
    ${({ theme }) => theme.spacing(11)}px;
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
interface VerificationRecordDetailsProps {
  paymentVerification: PaymentVerificationNode;
  canViewActivityLog: boolean;
}

export function VerificationRecordDetails({
  paymentVerification,
  canViewActivityLog,
}: VerificationRecordDetailsProps): React.ReactElement {
  return (
    <>
      <ContainerColumnWithBorder>
        <Title>
          <Typography variant='h6'>Payment Record Details</Typography>
        </Title>
        <Grid container spacing={3}>
          <Grid item xs={3}>
            <LabelizedField label='STATUS'>
              <StatusContainer>
                <StatusBox
                  status={paymentVerification.paymentRecord.status}
                  statusToColor={paymentRecordStatusToColor}
                />
              </StatusContainer>
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label='STATUS DATE'
              value={
                <UniversalMoment>
                  {paymentVerification.paymentRecord.statusDate}
                </UniversalMoment>
              }
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label='REGISTRATION GROUP'
              value={paymentVerification.paymentRecord.registrationCaId}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label='TARGET POPULATION'
              value={paymentVerification.paymentRecord.targetPopulation.name}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label='DISTRIBUTION MODALITY'
              value={paymentVerification.paymentRecord.distributionModality}
            />
          </Grid>
        </Grid>
      </ContainerColumnWithBorder>
      <ContainerColumnWithBorder>
        <Title>
          <Typography variant='h6'>Verification Details</Typography>
        </Title>
        <Grid container spacing={3}>
          <Grid item xs={3}>
            <LabelizedField label='STATUS'>
              <StatusContainer>
                <StatusBox
                  status={paymentVerification.status}
                  statusToColor={verificationRecordsStatusToColor}
                />
              </StatusContainer>
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label='STATUS DATE'
              value={
                <UniversalMoment>
                  {paymentVerification.statusDate}
                </UniversalMoment>
              }
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label='AMOUNT RECEIVED'
              value={formatCurrency(paymentVerification.receivedAmount)}
            />
          </Grid>
        </Grid>
      </ContainerColumnWithBorder>
      <Overview>
        <Title>
          <Typography variant='h6'>Household</Typography>
        </Title>
        <Grid container spacing={3}>
          <Grid item xs={3}>
            <LabelizedField
              label='HOUSEHOLD ID'
              value={paymentVerification.paymentRecord.household.unicefId}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label='HEAD OF HOUSEHOLD'
              value={paymentVerification.paymentRecord.fullName}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label='TOTAL PERSON COVERED'
              value={paymentVerification.paymentRecord.totalPersonsCovered}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label='PHONE NUMBER'
              value={
                paymentVerification.paymentRecord.household.headOfHousehold
                  .phoneNo
              }
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label='ALT. PHONE NUMBER'
              value={
                paymentVerification.paymentRecord.household.headOfHousehold
                  .phoneNoAlternative
              }
            />
          </Grid>
        </Grid>
      </Overview>
      <Overview>
        <Title>
          <Typography variant='h6'>Entitlement Details</Typography>
        </Title>
        <Grid container spacing={3}>
          <Grid item xs={3}>
            <LabelizedField
              label='ENTITLEMENT QUANTITY'
              value={paymentVerification.paymentRecord.entitlementQuantity}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label='DELIVERED QUANTITY'
              value={paymentVerification.paymentRecord.deliveredQuantity}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label='CURRENCY'
              value={paymentVerification.paymentRecord.currency}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label='DELIVERY TYPE'
              value={paymentVerification.paymentRecord.deliveryType}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label='DELIVERY DATE'
              value={
                <UniversalMoment>
                  {paymentVerification.paymentRecord.deliveryDate}
                </UniversalMoment>
              }
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label='ENTITLEMENT CARD ID'
              value={paymentVerification.paymentRecord.entitlementCardNumber}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label='TRANSACTION REFERENCE ID'
              value={paymentVerification.paymentRecord.transactionReferenceId}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label='ENTITLEMENT CARD ISSUE DATE'
              value={
                <UniversalMoment>
                  {paymentVerification.paymentRecord.entitlementCardIssueDate}
                </UniversalMoment>
              }
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label='FSP'
              value={paymentVerification.paymentRecord.serviceProvider.fullName}
            />
          </Grid>
        </Grid>
      </Overview>
      {canViewActivityLog && (
        <TableWrapper>
          <UniversalActivityLogTable objectId={paymentVerification.id} />
        </TableWrapper>
      )}
    </>
  );
}
