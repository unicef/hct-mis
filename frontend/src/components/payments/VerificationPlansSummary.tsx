import { Box, Grid, Typography } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { CashPlanQuery } from '../../__generated__/graphql';
import { LabelizedField } from '../core/LabelizedField';
import { paymentVerificationStatusToColor } from '../../utils/utils';
import { StatusBox } from '../core/StatusBox';
import { UniversalMoment } from '../core/UniversalMoment';
import { Title } from '../core/Title';

interface VerificationPlansSummaryProps {
  cashPlan: CashPlanQuery['cashPlan'];
}

export function VerificationPlansSummary({
  cashPlan,
}: VerificationPlansSummaryProps): React.ReactElement {
  const { t } = useTranslation();
  const {
    cashPlanPaymentVerificationSummary: {
      status,
      activationDate,
      completionDate,
    },
  } = cashPlan;

  return (
    <Grid container>
      <Grid item xs={9}>
        <Title>
          <Typography variant='h6'>
            {t('Verification Plans Summary')}
          </Typography>
        </Title>
        <Grid container>
          <Grid item xs={3}>
            <Box pt={2} pb={2}>
              <LabelizedField label={t('Status')}>
                <StatusBox
                  status={status}
                  statusToColor={paymentVerificationStatusToColor}
                />
              </LabelizedField>
            </Box>
          </Grid>
          <Grid item xs={3}>
            <Box pt={2} pb={2}>
              <LabelizedField label={t('Activation Date')}>
                <UniversalMoment>{activationDate}</UniversalMoment>
              </LabelizedField>
            </Box>
          </Grid>
          <Grid item xs={3}>
            <Box pt={2} pb={2}>
              <LabelizedField label={t('Completion Date')}>
                <UniversalMoment>{completionDate}</UniversalMoment>
              </LabelizedField>
            </Box>
          </Grid>
          <Grid item xs={3}>
            <Box pt={2} pb={2}>
              <LabelizedField label={t('Number of Verification Plans')}>
                {cashPlan.verifications.totalCount}
              </LabelizedField>
            </Box>
          </Grid>
        </Grid>
      </Grid>
    </Grid>
  );
}
