import { Box, Button, Grid, Typography } from '@material-ui/core';
import { GetApp } from '@material-ui/icons';
import DeleteIcon from '@material-ui/icons/Delete';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { hasPermissions, PERMISSIONS } from '../../config/permissions';
import { usePermissions } from '../../hooks/usePermissions';
import {
  choicesToDict,
  paymentVerificationStatusToColor,
} from '../../utils/utils';
import {
  CashPlanQuery,
  CashPlanVerificationSamplingChoicesQuery,
} from '../../__generated__/graphql';
import { ErrorButton } from '../core/ErrorButton';
import { LabelizedField } from '../core/LabelizedField';
import { StatusBox } from '../core/StatusBox';
import { UniversalMoment } from '../core/UniversalMoment';
import { ActivateVerificationPlan } from './ActivateVerificationPlan';
import { DiscardVerificationPlan } from './DiscardVerificationPlan';
import { EditVerificationPlan } from './EditVerificationPlan';
import { FinishVerificationPlan } from './FinishVerificationPlan';
import { ImportXlsx } from './ImportXlsx';
import { VerificationPlanDetailsChart } from './VerificationPlanChart';

interface VerificationPlanDetailsProps {
  verificationPlan: CashPlanQuery['cashPlan']['verifications']['edges'][number]['node'];
  samplingChoicesData: CashPlanVerificationSamplingChoicesQuery;
  cashPlan: CashPlanQuery['cashPlan'];
}

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

const StyledLink = styled.a`
  text-decoration: none;
`;

const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

const StatusContainer = styled.div`
  min-width: 120px;
  max-width: 200px;
`;

export const VerificationPlanDetails = ({
  verificationPlan,
  samplingChoicesData,
  cashPlan,
}: VerificationPlanDetailsProps): React.ReactElement => {
  const { t } = useTranslation();
  const permissions = usePermissions();
  if (!verificationPlan || !samplingChoicesData || !permissions) return null;

  const canEditAndActivateAndDelete = verificationPlan.status === 'PENDING';
  const canFinishAndDiscard = verificationPlan.status === 'ACTIVE';

  const canEdit =
    hasPermissions(PERMISSIONS.PAYMENT_VERIFICATION_UPDATE, permissions) &&
    canEditAndActivateAndDelete;
  const canActivate =
    hasPermissions(PERMISSIONS.PAYMENT_VERIFICATION_ACTIVATE, permissions) &&
    canEditAndActivateAndDelete;

  const canFinish =
    hasPermissions(PERMISSIONS.PAYMENT_VERIFICATION_FINISH, permissions) &&
    canFinishAndDiscard;
  const canDiscard =
    hasPermissions(PERMISSIONS.PAYMENT_VERIFICATION_DISCARD, permissions) &&
    canFinishAndDiscard;
  const canImport = hasPermissions(
    PERMISSIONS.PAYMENT_VERIFICATION_IMPORT,
    permissions,
  );
  const canExport = hasPermissions(
    PERMISSIONS.PAYMENT_VERIFICATION_EXPORT,
    permissions,
  );

  const samplingChoicesDict = choicesToDict(
    samplingChoicesData.cashPlanVerificationSamplingChoices,
  );

  const handleDelete = (): void => {
    console.log('DELETE VERIFICATION PLAN');
  };

  return (
    <Container>
      <Box display='flex' justifyContent='space-between'>
        <Title>
          <Typography variant='h6'>
            {t('Verification Plan')} #{verificationPlan.unicefId}
          </Typography>
        </Title>
        <Box display='flex' alignItems='center'>
          {canEditAndActivateAndDelete && (
            <>
              <Box mr={2}>
                <ErrorButton
                  onClick={() => handleDelete()}
                  startIcon={<DeleteIcon />}
                >
                  {t('Delete')}
                </ErrorButton>
              </Box>

              {canEdit && (
                <EditVerificationPlan
                  cashPlanId={cashPlan.id}
                  cashPlanVerificationId={verificationPlan.id}
                />
              )}
              {canActivate && (
                <Box alignItems='center' display='flex'>
                  {canActivate && (
                    <ActivateVerificationPlan
                      cashPlanVerificationId={verificationPlan.id}
                    />
                  )}
                </Box>
              )}
            </>
          )}
          {canFinishAndDiscard && (
            <Box display='flex'>
              {verificationPlan.verificationMethod === 'XLSX' && (
                <>
                  {canExport && (
                    <Box p={2}>
                      <StyledLink
                        download
                        href={`/api/download-cash-plan-payment-verification/${verificationPlan.id}`}
                      >
                        <Button
                          color='primary'
                          variant='outlined'
                          startIcon={<GetApp />}
                        >
                          {t('Export XLSX')}
                        </Button>
                      </StyledLink>
                    </Box>
                  )}
                  {canImport && (
                    <Box p={2}>
                      <ImportXlsx verificationPlanId={verificationPlan.id} />
                    </Box>
                  )}
                </>
              )}
              {canFinish && (
                <FinishVerificationPlan
                  cashPlanVerificationId={verificationPlan.id}
                />
              )}
              {canDiscard && (
                <DiscardVerificationPlan
                  cashPlanVerificationId={verificationPlan.id}
                />
              )}
            </Box>
          )}
        </Box>
      </Box>
      <Grid container>
        <Grid item xs={11}>
          <Grid container>
            <Grid item xs={3}>
              <LabelizedField label={t('STATUS')}>
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
                label: t('SAMPLING'),
                value: samplingChoicesDict[verificationPlan.sampling],
              },
              {
                label: t('RESPONDED'),
                value: verificationPlan.respondedCount,
              },
              {
                label: t('RECEIVED WITH ISSUES'),
                value: verificationPlan.receivedWithProblemsCount,
              },
              {
                label: t('VERIFICATION METHOD'),
                value: verificationPlan.verificationMethod,
              },
              {
                label: t('SAMPLE SIZE'),
                value: verificationPlan.sampleSize,
              },
              {
                label: t('RECEIVED'),
                value: verificationPlan.receivedCount,
              },
              {
                label: t('NOT RECEIVED'),
                value: verificationPlan.notReceivedCount,
              },
              {
                label: t('ACTIVATION DATE'),
                value: (
                  <UniversalMoment>
                    {verificationPlan.activationDate}
                  </UniversalMoment>
                ),
              },
              {
                label: t('COMPLETION DATE'),
                value: (
                  <UniversalMoment>
                    {verificationPlan.completionDate}
                  </UniversalMoment>
                ),
              },
            ].map((el) => (
              <Grid item xs={3} key={el.label}>
                <Box pt={2} pb={2}>
                  <LabelizedField label={el.label} value={el.value} />
                </Box>
              </Grid>
            ))}
          </Grid>
        </Grid>
        <Grid item xs={1}>
          <VerificationPlanDetailsChart verificationPlan={verificationPlan} />
        </Grid>
      </Grid>
    </Container>
  );
};
