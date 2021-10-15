import { Box, Grid, Paper, Typography } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { choicesToDict, formatCurrencyWithSymbol } from '../../utils/utils';
import {
  HouseholdChoiceDataQuery,
  HouseholdNode,
} from '../../__generated__/graphql';
import { ContentLink } from '../ContentLink';
import { CardAmount } from '../Dashboard/DashboardCard';
import { LabelizedField } from '../LabelizedField';
import {MiśTheme} from "../../theme";

const Container = styled.div`
  display: flex;
  flex: 1;
  width: 100%;
  background-color: #fff;
  padding: ${({ theme }) => theme.spacing(8)}px
    ${({ theme }) => theme.spacing(11)}px;
  flex-direction: column;
  align-items: center;
  border-color: #b1b1b5;
  border-bottom-width: 1px;
  border-bottom-style: solid;

  && > div {
    margin: 5px;
  }
`;

const Overview = styled.div`
  display: flex;
  flex-direction: row;
  width: 100%;
`;
const OverviewPaper = styled(Paper)`
  margin: 20px 20px 0 20px;
  padding: 20px ${({ theme }) => theme.spacing(11)}px;
`;
const Title = styled.div`
  width: 100%;
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;
const Label = styled.span`
  ${({ theme }: { theme: MiśTheme }) => theme.styledMixins.label}
`;

interface HouseholdDetailsProps {
  household: HouseholdNode;
  choicesData: HouseholdChoiceDataQuery;
}
export function HouseholdDetails({
  household,
  choicesData,
}: HouseholdDetailsProps): React.ReactElement {
  const { t } = useTranslation();
  const businessArea = useBusinessArea();
  const residenceChoicesDict = choicesToDict(
    choicesData.residenceStatusChoices,
  );
  return (
    <>
      <Container>
        <Title>
          <Typography variant='h6'>{t('Details')}</Typography>
        </Title>
        <Overview>
          <Grid container spacing={3}>
            <Grid item xs={3}>
              <LabelizedField label={t('Household Size')}>
                {household.size}
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label={t('Residence Status')}>
                {residenceChoicesDict[household.residenceStatus]}
              </LabelizedField>
            </Grid>
            <Grid item xs={6}>
              <LabelizedField label={t('Head of Household')}>
                <ContentLink
                  href={`/${businessArea}/population/individuals/${household.headOfHousehold.id}`}
                >
                  {household.headOfHousehold.fullName}
                </ContentLink>
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label={t('FEMALE CHILD HEADED HOUSEHOLD')}>
                {household.fchildHoh ? t('Yes') : t('No')}
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label={t('CHILD HEADED HOUSEHOLD')}>
                {household.childHoh ? t('Yes') : t('No')}
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label={t('Country')}>
                {household.country}
              </LabelizedField>
            </Grid>

            <Grid item xs={3}>
              <LabelizedField label={t('Country of Origin')}>
                {household.countryOrigin}
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label={t('Address')}>
                {household.address}
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label={t('Village')}>
                {household.village}
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label={t('Administrative Level 1')}>
                {household.admin1?.title}
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label={t('Administrative Level 2')}>
                {household.admin2?.title}
              </LabelizedField>
            </Grid>
            <Grid item xs={6}>
              <LabelizedField label={t('Geolocation')}>
                {household.geopoint
                  ? `${household.geopoint.coordinates[0]}, ${household.geopoint.coordinates[1]}`
                  : '-'}
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label={t('UNHCR CASE ID')}>
                {household?.unhcrId}
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label={t('LENGTH OF TIME SINCE ARRIVAL')}>
                {household.flexFields?.months_displaced_h_f}
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label={t('NUMBER OF TIMES DISPLACED')}>
                {household.flexFields?.number_times_displaced_h_f}
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label={t('IS THIS A RETURNEE HOUSEHOLD?')}>
                {household.returnee ? t('Yes') : t('No')}
              </LabelizedField>
            </Grid>
          </Grid>
        </Overview>
      </Container>
      <OverviewPaper>
        <Title>
          <Typography variant='h6'>{t('Benefits')}</Typography>
        </Title>
        <Grid container>
          <Grid item xs={4}>
            <Grid container>
              <Grid item xs={6}>
                <Label color='textSecondary'>
                  {t('PrOgRAmmE(S) ENROLLED')}
                </Label>
              </Grid>
              <Grid item xs={6}>
                <Label color='textSecondary'>{t('Cash received')}</Label>
              </Grid>
            </Grid>
            {household.programsWithDeliveredQuantity.length ? (
              household.programsWithDeliveredQuantity.map((item) => (
                <Grid container key={item.id}>
                  <Grid item xs={6}>
                    <ContentLink
                      href={`/${businessArea}/programs/${item.id}`}
                    >
                      {item.name}
                    </ContentLink>
                  </Grid>
                  <Grid item xs={6}>
                    <Box display='flex' flexDirection='column'>
                      {item.quantity.map((qty) => (
                        <Box
                          key={`${item.id}-${qty.currency}-${qty.totalDeliveredQuantity}`}
                        >
                          <CardAmount>
                            {formatCurrencyWithSymbol(
                              qty.totalDeliveredQuantity,
                              qty.currency,
                            )}
                          </CardAmount>
                        </Box>
                      ))}
                    </Box>
                  </Grid>
                </Grid>
              ))
            ) : (
              <Grid container>
                <Grid item xs={6}>
                  -
                </Grid>
                <Grid item xs={6}>
                  -
                </Grid>
              </Grid>
            )}
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label={t('Total Cash Received')}>
              <CardAmount>
                {formatCurrencyWithSymbol(
                  household.totalCashReceived,
                  household.currency,
                )}
              </CardAmount>
            </LabelizedField>
          </Grid>
        </Grid>
      </OverviewPaper>
    </>
  );
}
