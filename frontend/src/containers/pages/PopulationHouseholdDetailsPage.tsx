import React from 'react';
import styled from 'styled-components';
import Paper from '@material-ui/core/Paper';
import { Grid, Typography } from '@material-ui/core';
import { useParams } from 'react-router-dom';
import { HouseholdDetails } from '../../components/population/HouseholdDetails';
import { PageHeader } from '../../components/PageHeader';
import {
  HouseholdDetailedFragment,
  HouseholdNode,
  useHouseholdChoiceDataQuery,
  useHouseholdQuery,
} from '../../__generated__/graphql';
import { BreadCrumbsItem } from '../../components/BreadCrumbs';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { HouseholdVulnerabilities } from '../../components/population/HouseholdVulnerabilities';
import { LabelizedField } from '../../components/LabelizedField';
import { HouseholdIndividualsTable } from '../tables/HouseholdIndividualsTable';
import { UniversalActivityLogTable } from '../tables/UniversalActivityLogTable';
import { PaymentRecordHouseholdTable } from '../tables/PaymentRecordHouseholdTable';
import { UniversalMoment } from '../../components/UniversalMoment';
import { PermissionDenied } from '../../components/PermissionDenied';
import { hasPermissions, PERMISSIONS } from '../../config/permissions';
import { usePermissions } from '../../hooks/usePermissions';
import { LoadingComponent } from '../../components/LoadingComponent';
import { HouseholdCompositionTable } from '../tables/HouseholdCompositionTable';

const Container = styled.div`
  padding: 20px;
  && {
    display: flex;
    flex-direction: column;
    width: 100%;
  }
`;

const Title = styled.div`
  width: 100%;
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

const Overview = styled(Paper)`
  padding: ${({ theme }) => theme.spacing(8)}px
    ${({ theme }) => theme.spacing(11)}px;
  margin-top: 20px;
  &:first-child {
    margin-top: 0;
  }
`;
const Content = styled.div`
  margin-top: 20px;
`;

const SubTitle = styled(Typography)`
  && {
    font-size: 16px;
  }
`;

export function PopulationHouseholdDetailsPage(): React.ReactElement {
  const { id } = useParams();
  const businessArea = useBusinessArea();
  const permissions = usePermissions();

  const { data, loading } = useHouseholdQuery({
    variables: { id },
  });
  const {
    data: choicesData,
    loading: choicesLoading,
  } = useHouseholdChoiceDataQuery();

  if (loading || choicesLoading) return <LoadingComponent />;
  if (permissions === null) return null;

  if (
    permissions &&
    !hasPermissions(PERMISSIONS.POPULATION_VIEW_HOUSEHOLDS_DETAILS, permissions)
  )
    return <PermissionDenied />;

  if (!data || !choicesData) return null;

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: 'Households',
      to: `/${businessArea}/population/household`,
    },
  ];

  const { household } = data;

  return (
    <div>
      <PageHeader
        title={`Household ID: ${household.unicefId}`}
        breadCrumbs={breadCrumbsItems}
        withFlag={household.sanctionListPossibleMatch}
        withTriangle={household.hasDuplicates}
      />
      <HouseholdDetails
        choicesData={choicesData}
        household={household as HouseholdNode}
      />
      <HouseholdCompositionTable
        household={household as HouseholdDetailedFragment}
      />
      <Container>
        <HouseholdIndividualsTable
          choicesData={choicesData}
          household={household as HouseholdNode}
        />
        <PaymentRecordHouseholdTable
          openInNewTab
          household={household as HouseholdNode}
        />
        <HouseholdVulnerabilities
          household={household as HouseholdDetailedFragment}
        />
        <Overview>
          <Title>
            <Typography variant='h6'>Registration Details</Typography>
          </Title>
          <Grid container spacing={6}>
            <Grid item xs={3}>
              <LabelizedField label='Source'>
                <div>{household.registrationDataImport.dataSource}</div>
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label='Import name'>
                <div>{household.registrationDataImport.name}</div>
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label='Registered Date'>
                <div>
                  <UniversalMoment>
                    {household.registrationDataImport.importDate}
                  </UniversalMoment>
                </div>
              </LabelizedField>
            </Grid>
          </Grid>
          <hr />
          <SubTitle variant='h6'>Data Collection</SubTitle>
          <Grid container spacing={6}>
            <Grid item xs={3}>
              <LabelizedField label='Start time'>
                <div>-</div>
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label='End time'>
                <div>-</div>
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label='Device ID'>
                <div>-</div>
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label='User name'>
                {household.registrationDataImport.importedBy.email}
              </LabelizedField>
            </Grid>
          </Grid>
        </Overview>
        <Content>
          <UniversalActivityLogTable objectId={data.household.id} />
        </Content>
      </Container>
    </div>
  );
}
