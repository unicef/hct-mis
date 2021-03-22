import React from 'react';
import styled from 'styled-components';
import { Typography, Grid } from '@material-ui/core';
import { LabelizedField } from '../../../../components/LabelizedField';
import {
  HouseholdChoiceDataQuery,
  ImportedHouseholdDetailedFragment,
} from '../../../../__generated__/graphql';
import { choicesToDict } from '../../../../utils/utils';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { ContainerColumnWithBorder } from '../../../../components/ContainerColumnWithBorder';
import { ContentLink } from '../../../../components/ContentLink';

const Overview = styled.div`
  display: flex;
  flex-direction: row;
  width: 100%;
`;
const Title = styled.div`
  width: 100%;
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

interface HouseholdDetailsProps {
  household: ImportedHouseholdDetailedFragment;
  choicesData: HouseholdChoiceDataQuery;
}
export function HouseholdDetails({
  household,
  choicesData,
}: HouseholdDetailsProps): React.ReactElement {
  const businessArea = useBusinessArea();

  const residenceChoicesDict = choicesToDict(
    choicesData.residenceStatusChoices,
  );
  return (
    <ContainerColumnWithBorder>
      <Title>
        <Typography variant='h6'>Details</Typography>
      </Title>
      <Overview>
        <Grid container spacing={6}>
          <Grid item xs={3}>
            <LabelizedField label='Household Size'>
              {household.size}
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField label='Country'>
              {household.country}
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField label='Residence Status'>
              {residenceChoicesDict[household.residenceStatus]}
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField label='Country of Origin'>
              {household.countryOrigin}
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField label='Head of Household'>
              <ContentLink
                href={`/${businessArea}/registration-data-import/individual/${household.headOfHousehold.id}`}
              >
                {household.headOfHousehold.fullName}
              </ContentLink>
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField label='ADMINISTRATIVE LEVEL 1'>
              {household.admin1Title}
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField label='ADMINISTRATIVE LEVEL 2'>
              {household.admin2Title}
            </LabelizedField>
          </Grid>
        </Grid>
      </Overview>
    </ContainerColumnWithBorder>
  );
}
