import React from 'react';
import styled from 'styled-components';
import { Grid, Paper, Typography } from '@material-ui/core';
import { LabelizedField } from '../LabelizedField';
import {
  IndividualNode,
  useHouseholdChoiceDataQuery,
} from '../../__generated__/graphql';
import {
  getAgeFromDob,
  sexToCapitalize,
  choicesToDict,
} from '../../utils/utils';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { LoadingComponent } from '../LoadingComponent';
import { UniversalMoment } from '../UniversalMoment';
import { ContentLink } from '../ContentLink';

const Overview = styled(Paper)`
  padding: ${({ theme }) => theme.spacing(8)}px
    ${({ theme }) => theme.spacing(11)}px;
`;

const Title = styled.div`
  width: 100%;
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

const BorderBox = styled.div`
  border-bottom: 1px solid #e1e1e1;
`;

interface IndividualBioDataProps {
  individual: IndividualNode;
}
export function IndividualsBioData({
  individual,
}: IndividualBioDataProps): React.ReactElement {
  const businessArea = useBusinessArea();

  let age: number | null;
  const { birthDate } = individual;
  if (birthDate) {
    age = getAgeFromDob(birthDate);
  }

  const {
    data: choicesData,
    loading: choicesLoading,
  } = useHouseholdChoiceDataQuery();

  if (choicesLoading) {
    return <LoadingComponent />;
  }
  const relationshipChoicesDict = choicesToDict(
    choicesData.relationshipChoices,
  );
  const maritalStatusChoicesDict = choicesToDict(
    choicesData.maritalStatusChoices,
  );
  const roleChoicesDict = choicesToDict(choicesData.roleChoices);
  const mappedIndividualDocuments = individual.documents?.edges?.map((edge) => (
    <Grid item xs={3} key={edge.node.id}>
      <LabelizedField label={edge.node.type.label}>
        {edge.node.documentNumber}
      </LabelizedField>
    </Grid>
  ));
  const mappedIdentities = individual.identities?.map((item) => (
    <Grid item xs={3} key={item.id}>
      <LabelizedField label={`${item.type} ID`}>{item.number}</LabelizedField>
    </Grid>
  ));

  return (
    <Overview>
      <Title>
        <Typography variant='h6'>Bio Data</Typography>
      </Title>
      <Grid container spacing={6}>
        <Grid item xs={3}>
          <LabelizedField label='Full Name'>
            {individual.fullName}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label='Given Name'>
            {individual.givenName}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label='Middle Name'>
            {individual.middleName}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label='Family Name'>
            {individual.familyName}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label='Gender'>
            {sexToCapitalize(individual.sex)}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label='Age'>{age}</LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label='Date of Birth'>
            <UniversalMoment>{birthDate}</UniversalMoment>
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label='Estimated Date of Birth'>
            {individual.estimatedBirthDate
              ? individual.estimatedBirthDate
              : 'No'}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label='Marital Status'>
            {maritalStatusChoicesDict[individual.maritalStatus]}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label='Pregnant'>
            {individual.pregnant ? 'Yes' : 'No'}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label='Household ID'>
            {individual.household?.id ? (
              <ContentLink
                href={`/${businessArea}/population/household/${individual.household?.id}`}
              >
                {individual.household?.unicefId}
              </ContentLink>
            ) : (
              <span>-</span>
            )}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label='Role'>
            {roleChoicesDict[individual.role]}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label='Relationship to HOH'>
            {relationshipChoicesDict[individual.relationship]}
          </LabelizedField>
        </Grid>
        {!mappedIndividualDocuments.length &&
        !mappedIdentities.length ? null : (
          <Grid item xs={12}>
            <BorderBox />
          </Grid>
        )}
        {mappedIndividualDocuments}
        {mappedIdentities}
        <Grid item xs={12}>
          <BorderBox />
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label='Phone Number'>
            {individual.phoneNo}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label='Alternate Phone Number'>
            {individual.phoneNoAlternative}
          </LabelizedField>
        </Grid>
        <Grid item xs={12}>
          <BorderBox />
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label='Date of last screening against sanctions list'>
            <UniversalMoment>
              {individual.sanctionListLastCheck}
            </UniversalMoment>
          </LabelizedField>
        </Grid>
      </Grid>
    </Overview>
  );
}
