import { Grid, Paper, Typography } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { PaymentQuery } from '../../../__generated__/graphql';
import { UniversalActivityLogTable } from '../../../containers/tables/UniversalActivityLogTable';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import {
  formatCurrencyWithSymbol,
  getPhoneNoLabel,
  paymentStatusDisplayMap,
  paymentStatusToColor,
  verificationRecordsStatusToColor,
} from '../../../utils/utils';
import { BlackLink } from '../../core/BlackLink';
import { ContainerColumnWithBorder } from '../../core/ContainerColumnWithBorder';
import { DividerLine } from '../../core/DividerLine';
import { LabelizedField } from '../../core/LabelizedField';
import { StatusBox } from '../../core/StatusBox';
import { Title } from '../../core/Title';
import { UniversalMoment } from '../../core/UniversalMoment';

const Overview = styled(Paper)`
  margin: 20px;
  padding: ${({ theme }) => theme.spacing(8)}px
    ${({ theme }) => theme.spacing(11)}px;
`;

interface PaymentDetailsProps {
  payment: PaymentQuery['payment'];
  canViewActivityLog: boolean;
  canViewHouseholdDetails: boolean;
}

export const PaymentDetails = ({
  payment,
  canViewActivityLog,
  canViewHouseholdDetails,
}: PaymentDetailsProps): React.ReactElement => {
  const businessArea = useBusinessArea();
  const { t } = useTranslation();
  let paymentVerification: PaymentQuery['payment']['verification'] = null;
  if (payment.verification && payment.verification.status !== 'PENDING') {
    paymentVerification = payment.verification;
  }
  return (
    <>
      <ContainerColumnWithBorder>
        <Title>
          <Typography variant='h6'>{t('Details')}</Typography>
        </Title>
        <Grid container spacing={3}>
          <Grid item xs={3}>
            <LabelizedField label={t('STATUS')}>
              <StatusBox
                status={payment.status}
                statusToColor={paymentStatusToColor}
                statusNameMapping={paymentStatusDisplayMap}
              />
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('ENTITLEMENT QUANTITY')}
              value={payment.entitlementQuantity}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('DELIVERED QUANTITY')}
              value={payment.deliveredQuantity}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField label={t('CURRENCY')} value={payment.currency} />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('DELIVERY DATE')}
              value={<UniversalMoment>{payment.deliveryDate}</UniversalMoment>}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField label={t('TARGET POPULATION')}>
              <BlackLink
                to={`/${businessArea}/target-population/${payment.targetPopulation.id}`}
              >
                {payment.targetPopulation?.name}
              </BlackLink>
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('DISTRIBUTION MODALITY')}
              value={payment.distributionModality}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('Related Payment Id')}
              value={payment.sourcePayment?.unicefId}
            />
          </Grid>
        </Grid>
      </ContainerColumnWithBorder>
      {paymentVerification != null ? (
        <ContainerColumnWithBorder>
          <Title>
            <Typography variant='h6'>{t('Verification Details')}</Typography>
          </Title>
          <Grid container spacing={3}>
            <Grid item xs={3}>
              <LabelizedField label={t('STATUS')}>
                <StatusBox
                  status={paymentVerification.status}
                  statusToColor={verificationRecordsStatusToColor}
                />
              </LabelizedField>
            </Grid>

            <Grid item xs={3}>
              <LabelizedField
                label={t('AMOUNT RECEIVED')}
                value={formatCurrencyWithSymbol(
                  paymentVerification.receivedAmount,
                  payment.currency,
                )}
              />
            </Grid>
          </Grid>
        </ContainerColumnWithBorder>
      ) : null}
      <Overview>
        <Title>
          <Typography variant='h6'>{t('Household')}</Typography>
        </Title>
        <Grid container spacing={3}>
          <Grid item xs={3}>
            <LabelizedField label={t('HOUSEHOLD ID')}>
              {payment.household?.id ? (
                <BlackLink
                  to={
                    canViewHouseholdDetails
                      ? `/${businessArea}/population/household/${payment.household.id}`
                      : undefined
                  }
                >
                  {payment.household.unicefId}
                </BlackLink>
              ) : (
                '-'
              )}
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t("Collector's Name")}
              value={payment.snapshotCollectorFullName}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t("Collector's ID")}
              value={payment.collector?.unicefId}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('TOTAL PERSON COVERED')}
              value={payment.household.size}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('PHONE NUMBER')}
              value={getPhoneNoLabel(
                payment.collector.phoneNo,
                payment.collector.phoneNoValid,
              )}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('ALT. PHONE NUMBER')}
              value={getPhoneNoLabel(
                payment.collector.phoneNoAlternative,
                payment.collector.phoneNoAlternativeValid,
              )}
            />
          </Grid>
        </Grid>
      </Overview>
      <Overview>
        <Title>
          <Typography variant='h6'>{t('Entitlement Details')}</Typography>
        </Title>
        <Grid container spacing={3}>
          <Grid item xs={3}>
            <LabelizedField
              label={t('DELIVERY MECHANISM')}
              value={payment.deliveryType}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('FSP')}
              value={payment.serviceProvider?.fullName}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('TRANSACTION REFERENCE ID')}
              value={payment.transactionReferenceId}
            />
          </Grid>
        </Grid>
        <DividerLine />
        <Grid container spacing={3}>
          <Grid item xs={3}>
            <LabelizedField
              label={t('Bank Name')}
              value={payment.snapshotCollectorBankName}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('Bank Account Number')}
              value={payment.snapshotCollectorBankAccountNumber}
            />
          </Grid>
        </Grid>
      </Overview>
      <Overview>
        <Title>
          <Typography variant='h6'>{t('Reconciliation Details')}</Typography>
        </Title>
        <Grid container spacing={3}>
          <Grid item xs={3}>
            <LabelizedField
              label={t("Collector's Name")}
              value={payment.additionalCollectorName}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('Document Type')}
              value={payment.additionalDocumentType}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('Document Number')}
              value={payment.additionalDocumentNumber}
            />
          </Grid>
        </Grid>
        <DividerLine />
        <Grid container spacing={3}>
          <Grid item xs={3}>
            <LabelizedField
              label={t('Failure Reason')}
              value={payment.reasonForUnsuccessfulPayment}
            />
          </Grid>
          <Grid item xs={3}>
            <LabelizedField
              label={t('Bank Account Number')}
              value={payment.snapshotCollectorBankAccountNumber}
            />
          </Grid>
        </Grid>
      </Overview>
      {canViewActivityLog && (
        <UniversalActivityLogTable objectId={payment.id} />
      )}
    </>
  );
};
