import { Grid, Typography } from '@material-ui/core';
import { Field } from 'formik';
import React from 'react';
import { useTranslation } from 'react-i18next';
import CalendarTodayRoundedIcon from '@material-ui/icons/CalendarTodayRounded';
import { FormikDateField } from '../../../../shared/Formik/FormikDateField';
import { OverviewContainer } from '../../../core/OverviewContainer';
import { PaperContainer } from '../../../targeting/PaperContainer';
import { Title } from '../../../core/Title';
import { FormikCurrencyAutocomplete } from '../../../../shared/FormikCurrencyAutocomplete';

interface PaymentPlanParametersProps {
  values;
}
const tomorrow = new Date().setDate(new Date().getDate() + 1);

export const PaymentPlanParameters = ({
  values,
}: PaymentPlanParametersProps): React.ReactElement => {
  const { t } = useTranslation();

  return (
    <PaperContainer>
      <Title>
        <Typography variant='h6'>{t('Parameters')}</Typography>
      </Title>
      <OverviewContainer>
        <Grid spacing={3} container>
          <Grid item xs={4}>
            <Field
              name='startDate'
              label={t('Start Date')}
              component={FormikDateField}
              required
              fullWidth
              decoratorEnd={<CalendarTodayRoundedIcon color='disabled' />}
              data-cy='input-start-date'
            />
          </Grid>
          <Grid item xs={4}>
            <Field
              name='endDate'
              label={t('End Date')}
              component={FormikDateField}
              required
              minDate={values.startDate}
              disabled={!values.startDate}
              initialFocusedDate={values.startDate}
              fullWidth
              decoratorEnd={<CalendarTodayRoundedIcon color='disabled' />}
              data-cy='input-end-date'
            />
          </Grid>

          <Grid item xs={4}>
            <Field
              name='currency'
              component={FormikCurrencyAutocomplete}
              required
            />
          </Grid>
          <Grid item xs={4}>
            <Field
              name='dispersionStartDate'
              label={t('Dispersion Start Date')}
              component={FormikDateField}
              required
              fullWidth
              decoratorEnd={<CalendarTodayRoundedIcon color='disabled' />}
              data-cy='input-dispersion-start-date'
            />
          </Grid>
          <Grid item xs={4}>
            <Field
              name='dispersionEndDate'
              label={t('Dispersion End Date')}
              component={FormikDateField}
              required
              minDate={tomorrow}
              disabled={!values.dispersionStartDate}
              initialFocusedDate={values.dispersionStartDate}
              fullWidth
              decoratorEnd={<CalendarTodayRoundedIcon color='disabled' />}
              data-cy='input-dispersion-end-date'
            />
          </Grid>
        </Grid>
      </OverviewContainer>
    </PaperContainer>
  );
};
