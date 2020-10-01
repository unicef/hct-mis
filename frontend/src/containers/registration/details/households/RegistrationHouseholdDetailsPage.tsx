import React from 'react';
import styled from 'styled-components';
import { useParams } from 'react-router-dom';
import { PageHeader } from '../../../../components/PageHeader';
import {
  useHouseholdChoiceDataQuery,
  useImportedHouseholdQuery,
} from '../../../../__generated__/graphql';
import { BreadCrumbsItem } from '../../../../components/BreadCrumbs';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { decodeIdString } from '../../../../utils/utils';
import { ImportedIndividualsTable } from '../../tables/ImportedIndividualsTable';
import { UniversalMoment } from '../../../../components/UniversalMoment';
import { HouseholdDetails } from './HouseholdDetails';
import { RegistrationDetails } from './RegistrationDetails';

const Container = styled.div`
  padding: 20px;
  && {
    display: flex;
    flex-direction: column;
    width: 100%;
  }
`;

export function RegistrationHouseholdDetailsPage(): React.ReactElement {
  const { id } = useParams();
  const businessArea = useBusinessArea();
  const { data, loading } = useImportedHouseholdQuery({
    variables: { id },
  });
  const {
    data: choicesData,
    loading: choicesLoading,
  } = useHouseholdChoiceDataQuery();
  if (loading || choicesLoading) return null;

  const { importedHousehold } = data;
  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: 'Registration Data import',
      to: `/${businessArea}/registration-data-import/`,
    },
    {
      title: importedHousehold.registrationDataImport.name,
      to: `/${businessArea}/registration-data-import/${btoa(
        `RegistrationDataImportNode:${importedHousehold.registrationDataImport.hctId}`,
      )}`,
    },
  ];

  return (
    <div>
      <PageHeader
        title={`Household ID: ${decodeIdString(id)}`}
        breadCrumbs={breadCrumbsItems}
      />
      <HouseholdDetails
        choicesData={choicesData}
        household={importedHousehold}
      />
      <Container>
        <ImportedIndividualsTable
          household={importedHousehold.id}
          isOnPaper
          rowsPerPageOptions={[5, 10, 15]}
          title='Individuals in Household'
        />
        <RegistrationDetails
          hctId={importedHousehold.registrationDataImport.hctId}
          registrationDate={`${(
            <UniversalMoment>
              {importedHousehold.firstRegistrationDate}
            </UniversalMoment>
          )}`}
        />
      </Container>
    </div>
  );
}
