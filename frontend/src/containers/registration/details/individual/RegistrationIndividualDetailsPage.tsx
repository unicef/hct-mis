import React from 'react';
import styled from 'styled-components';
import { useParams } from 'react-router-dom';
import { PageHeader } from '../../../../components/PageHeader';
import { BreadCrumbsItem } from '../../../../components/BreadCrumbs';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { decodeIdString } from '../../../../utils/utils';
import { useImportedIndividualQuery } from '../../../../__generated__/graphql';
import { usePermissions } from '../../../../hooks/usePermissions';
import { LoadingComponent } from '../../../../components/LoadingComponent';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { PermissionDenied } from '../../../../components/PermissionDenied';
import { RegistrationIndividualsBioData } from './RegistrationIndividualBioData';
import { RegistrationIndividualVulnerabilities } from './RegistrationIndividualVulnerabilities';

const Container = styled.div`
  padding: 20px;
  && {
    display: flex;
    flex-direction: column;
    width: 100%;
  }
`;

export function RegistrationIndividualDetailsPage(): React.ReactElement {
  const { id } = useParams();
  const businessArea = useBusinessArea();
  const permissions = usePermissions();
  const { data, loading } = useImportedIndividualQuery({
    variables: {
      id,
    },
  });

  if (loading) return <LoadingComponent />;
  if (permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.RDI_VIEW_DETAILS, permissions))
    return <PermissionDenied />;
  if (!data) return null;

  const { importedIndividual } = data;
  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: 'Registration Data import',
      to: `/${businessArea}/registration-data-import/`,
    },
    {
      title: importedIndividual.registrationDataImport.name,
      to: `/${businessArea}/registration-data-import/${btoa(
        `RegistrationDataImportNode:${importedIndividual.registrationDataImport.hctId}`,
      )}`,
    },
    {
      title: `HOUSEHOLD ID: ${decodeIdString(importedIndividual.household.id)}`,
      to: `/${businessArea}/registration-data-import/household/${importedIndividual.household.id}`,
    },
  ];

  return (
    <div>
      <PageHeader
        title={`Individual ID: ${decodeIdString(id)}`}
        breadCrumbs={breadCrumbsItems}
      />
      <Container>
        <RegistrationIndividualsBioData individual={importedIndividual} />
        <RegistrationIndividualVulnerabilities
          individual={importedIndividual}
        />
      </Container>
    </div>
  );
}
