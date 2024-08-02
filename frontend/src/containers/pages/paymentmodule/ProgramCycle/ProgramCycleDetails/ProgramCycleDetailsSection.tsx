import React from 'react';
import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { Title } from '@core/Title';
import { Typography } from '@mui/material';
import { OverviewContainer } from '@core/OverviewContainer';
import Grid from '@mui/material/Grid';
import { StatusBox } from '@core/StatusBox';
import { programCycleStatusToColor } from '@utils/utils';
import { LabelizedField } from '@core/LabelizedField';
import { Missing } from '@core/Missing';
import { UniversalMoment } from '@core/UniversalMoment';
import { ProgramCycle } from '@api/programCycleApi';
import { useTranslation } from 'react-i18next';

interface ProgramCycleDetailsSectionProps {
  programCycle: ProgramCycle;
}

export const ProgramCycleDetailsSection = ({
  programCycle,
}: ProgramCycleDetailsSectionProps): React.ReactElement => {
  const { t } = useTranslation();
  return (
    <Grid item xs={12}>
      <ContainerColumnWithBorder>
        <Title>
          <Typography variant="h6">{t('Details')}</Typography>
        </Title>
        <OverviewContainer>
          <Grid container spacing={6}>
            <Grid item xs={12}>
              <StatusBox
                status={programCycle.status}
                statusToColor={programCycleStatusToColor}
              />
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label={t('Created By')}>
                <Missing />
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label={t('Start Date')}>
                <UniversalMoment>{programCycle.start_date}</UniversalMoment>
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label={t('End Date')}>
                <UniversalMoment>{programCycle.end_date}</UniversalMoment>
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label={t('Programme Start Date')}>
                <Missing />
                {/*<UniversalMoment>{programStartDate}</UniversalMoment>*/}
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label={t('Programme End Date')}>
                <Missing />
                {/*<UniversalMoment>{programEndDate}</UniversalMoment>*/}
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label={t('Frequency of Payment')}>
                <Missing />
              </LabelizedField>
            </Grid>
          </Grid>
        </OverviewContainer>
      </ContainerColumnWithBorder>
    </Grid>
  );
};
