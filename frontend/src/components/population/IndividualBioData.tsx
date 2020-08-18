import React from 'react';
import styled from 'styled-components';
import { Grid, Paper, Typography } from '@material-ui/core';
import { useHistory } from 'react-router-dom';
import Moment from 'react-moment';
import { LabelizedField } from '../LabelizedField';
import { IndividualNode } from '../../__generated__/graphql';
import {
  decodeIdString,
  getAgeFromDob,
  sexToCapitalize,
} from '../../utils/utils';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { Missing } from '../Missing';
import { StatusBox } from '../StatusBox';

const Overview = styled(Paper)`
  padding: ${({ theme }) => theme.spacing(8)}px
    ${({ theme }) => theme.spacing(11)}px;
`;

const Title = styled.div`
  width: 100%;
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

const ContentLink = styled.div`
  text-decoration: underline;
  cursor: pointer;
`;
const StatusContainer = styled.div`
  min-width: 120px;
  max-width: 200px;
`;

interface IndividualBioDataProps {
  individual: IndividualNode;
}
export function IndividualsBioData({
  individual,
}: IndividualBioDataProps): React.ReactElement {
  const history = useHistory();
  const businessArea = useBusinessArea();

  let age: number | null;
  const { birthDate } = individual;
  if (birthDate) {
    age = getAgeFromDob(birthDate);
  }

  const openHousehold = (): void => {
    history.push(
      `/${businessArea}/population/household/${individual.household.id}`,
    );
  };

  const mappedIndividualDocuments = individual.documents?.edges?.map((edge) => (
    <Grid item xs={3}>
      <LabelizedField label={edge.node.type.label}>
        <div>{edge.node.documentNumber}</div>
      </LabelizedField>
    </Grid>
  ));
  const mappedIdentities = individual.identities?.map((item) => (
    <Grid item xs={3}>
      <LabelizedField label={`${item.type} ID`}>
        <div>{item.number}</div>
      </LabelizedField>
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
            <div>{individual.fullName}</div>
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label='Given Name'>
            <div>{individual.givenName}</div>
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label='Middle Name'>
            <div>{individual.middleName || '-'}</div>
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label='Family Name'>
            <div>{individual.familyName}</div>
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label='Sex'>
            <div>{sexToCapitalize(individual.sex)}</div>
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label='Age'>
            <div>{age}</div>
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label='Date of Birth'>
            <Moment format='DD/MM/YYYY'>{birthDate}</Moment>
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label='Estimated Date of Birth'>
            <div>
              {individual.estimatedBirthDate
                ? individual.estimatedBirthDate
                : 'No'}
            </div>
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label='Household ID'>
            <ContentLink onClick={() => openHousehold()}>
              {decodeIdString(individual.household.id)}
            </ContentLink>
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label='Role'>
            <div>{individual.role}</div>
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label='Relationship to HOH'>
            <div>{individual.relationship}</div>
          </LabelizedField>
        </Grid>
        {mappedIndividualDocuments}
        {mappedIdentities}
        <Grid item xs={3}>
          <LabelizedField label='Marital Status'>
            <div>{individual.maritalStatus}</div>
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label='Pregnant'>
            <div>
              <Missing />
              {/* <div>{individual.pregnant ? 'YES' : 'NO' || '-'}</div> */}
            </div>
          </LabelizedField>
        </Grid>
      </Grid>
    </Overview>
  );
}
