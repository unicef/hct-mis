import { Grid, Typography } from '@mui/material';
import React from 'react';
import { Pie } from 'react-chartjs-2';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { MiśTheme } from '../../../../theme';
import { PaymentPlanQuery } from '../../../../__generated__/graphql';
import { LabelizedField } from '../../../core/LabelizedField';
import { PaperContainer } from '../../../targeting/PaperContainer';
import { FieldBorder } from '../../../core/FieldBorder';

const colors = {
  femaleChildren: '#5F02CF',
  maleChildren: '#1D6A64',
  femaleAdult: '#DFCCF5',
  maleAdult: '#B1E3E0',
};

const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(2)}px;
`;

const ContentWrapper = styled.div`
  display: flex;
`;

const SummaryBorder = styled.div`
  padding: ${({ theme }) => theme.spacing(4)}px;
  border-color: #b1b1b5;
  border-left-width: 1px;
  border-left-style: solid;
`;

const SummaryValue = styled.div`
  font-family: ${({ theme }: { theme: MiśTheme }) =>
    theme.hctTypography.fontFamily};
  color: #253b46;
  font-size: 36px;
  line-height: 32px;
  margin-top: ${({ theme }) => theme.spacing(2)}px;
`;

const ChartContainer = styled.div`
  width: 100px;
  height: 100px;
  margin: 0 auto;
`;

interface PaymentPlanDetailsResultsProps {
  paymentPlan: PaymentPlanQuery['paymentPlan'];
}

export const PaymentPlanDetailsResults = ({
  paymentPlan,
}: PaymentPlanDetailsResultsProps): React.ReactElement => {
  const { t } = useTranslation();
  const {
    femaleChildrenCount,
    maleChildrenCount,
    femaleAdultsCount,
    maleAdultsCount,
    totalHouseholdsCount,
    totalIndividualsCount,
  } = paymentPlan;

  return (
    <>
      <PaperContainer>
        <Title>
          <Typography variant="h6">{t('Results')}</Typography>
        </Title>
        <ContentWrapper>
          <Grid container>
            <Grid item xs={4}>
              <Grid container spacing={3} justifyContent="flex-start">
                <Grid item xs={6}>
                  <FieldBorder color={colors.femaleChildren}>
                    <LabelizedField
                      label={t('Female Children')}
                      value={femaleChildrenCount}
                    />
                  </FieldBorder>
                </Grid>
                <Grid item xs={6}>
                  <FieldBorder color={colors.femaleAdult}>
                    <LabelizedField
                      label={t('Female Adults')}
                      value={femaleAdultsCount}
                    />
                  </FieldBorder>
                </Grid>
                <Grid item xs={6}>
                  <FieldBorder color={colors.maleChildren}>
                    <LabelizedField
                      label={t('Male Children')}
                      value={maleChildrenCount}
                    />
                  </FieldBorder>
                </Grid>
                <Grid item xs={6}>
                  <FieldBorder color={colors.maleAdult}>
                    <LabelizedField
                      label={t('Male Adults')}
                      value={maleAdultsCount}
                    />
                  </FieldBorder>
                </Grid>
              </Grid>
            </Grid>
            <Grid item xs={4}>
              <Grid
                container
                spacing={0}
                justifyContent="flex-start"
                alignItems="center"
              >
                <Grid item xs={4}>
                  <ChartContainer data-cy="chart-container">
                    <Pie
                      width={100}
                      height={100}
                      options={{
                        legend: {
                          display: false,
                        },
                      }}
                      data={{
                        labels: [
                          t('Female Children'),
                          t('Female Adults'),
                          t('Male Children'),
                          t('Male Adults'),
                        ],
                        datasets: [
                          {
                            data: [
                              femaleChildrenCount,
                              femaleAdultsCount,
                              maleChildrenCount,
                              maleAdultsCount,
                            ],
                            backgroundColor: [
                              colors.femaleChildren,
                              colors.femaleAdult,
                              colors.maleChildren,
                              colors.maleAdult,
                            ],
                          },
                        ],
                      }}
                    />
                  </ChartContainer>
                </Grid>
              </Grid>
            </Grid>
            <Grid item xs={4}>
              <Grid container spacing={0} justifyContent="flex-end">
                <Grid item xs={6}>
                  <SummaryBorder>
                    <LabelizedField label={t('Total Number of Households')}>
                      <SummaryValue>{totalHouseholdsCount || '0'}</SummaryValue>
                    </LabelizedField>
                  </SummaryBorder>
                </Grid>
                <Grid item xs={6}>
                  <SummaryBorder>
                    <LabelizedField label={t('Targeted Individuals')}>
                      <SummaryValue>
                        {totalIndividualsCount || '0'}
                      </SummaryValue>
                    </LabelizedField>
                  </SummaryBorder>
                </Grid>
              </Grid>
            </Grid>
          </Grid>
        </ContentWrapper>
      </PaperContainer>
    </>
  );
};
