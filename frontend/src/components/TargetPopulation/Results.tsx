import React from 'react';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';
import { Typography, Paper, Grid } from '@material-ui/core';
import { MiśTheme } from '../../theme';
import { LabelizedField } from '../LabelizedField';

const colors = {
  femaleChildren: '#023E90',
  maleChildren: '#029BFE',
  femaleAdult: '#73C302',
  maleAdult: '#F2E82C',
};

const PaperContainer = styled(Paper)`
  padding: ${({ theme }) => theme.spacing(3)}px
    ${({ theme }) => theme.spacing(4)}px;
  margin: ${({ theme }) => theme.spacing(5)}px;
  border-bottom: 1px solid rgba(224, 224, 224, 1);
`;

const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(2)}px;
`;

const ContentWrapper = styled.div`
  display: flex;
`;

const FieldBorder = styled.div`
  padding: 0 ${({ theme }) => theme.spacing(2)}px;
  border-color: ${(props) => props.color};
  border-left-width: 2px;
  border-left-style: solid;
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

const Label = styled.p`
  color: #b1b1b5;
`

interface ResultsProps {
  resultsData?;
}

export function Results({ resultsData }: ResultsProps) {
  const { t } = useTranslation();

  return (
    <div>
      <PaperContainer>
        <Title>
          <Typography variant='h6'>{t('Results')}</Typography>
        </Title>
        <ContentWrapper>
          {resultsData ? (
            <>
              <Grid container spacing={0} justify='flex-start'>
                <Grid item xs={6}>
                  <FieldBorder color={colors.femaleChildren}>
                    <LabelizedField
                      label='Female Children'
                      value={resultsData.femaleChildren}
                    />
                  </FieldBorder>
                </Grid>
                <Grid item xs={6}>
                  <FieldBorder color={colors.femaleAdult}>
                    <LabelizedField
                      label='Female Adults'
                      value={resultsData.femaleAdults}
                    />
                  </FieldBorder>
                </Grid>
                <Grid item xs={6}>
                  <FieldBorder color={colors.maleChildren}>
                    <LabelizedField
                      label='Male Children'
                      value={resultsData.maleChildren}
                    />
                  </FieldBorder>
                </Grid>
                <Grid item xs={6}>
                  <FieldBorder color={colors.maleAdult}>
                    <LabelizedField
                      label='Male Adults'
                      value={resultsData.maleAdults}
                    />
                  </FieldBorder>
                </Grid>
              </Grid>
              <SummaryBorder>
                <LabelizedField label='Total Number of Households'>
                  <SummaryValue>
                    {resultsData.totalNumberOfHouseholds}
                  </SummaryValue>
                </LabelizedField>
              </SummaryBorder>
              <SummaryBorder>
                <LabelizedField label='Targeted Individuals'>
                  <SummaryValue>{resultsData.targetedIndividuals}</SummaryValue>
                </LabelizedField>
              </SummaryBorder>
            </>
          ) : (
            <Label>Add targeting criteria to see results.</Label>
          )}
        </ContentWrapper>
      </PaperContainer>
    </div>
  );
}
