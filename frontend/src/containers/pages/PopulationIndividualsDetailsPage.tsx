import React from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import { BreadCrumbsItem } from '../../components/BreadCrumbs';
import { LoadingComponent } from '../../components/LoadingComponent';
import { PageHeader } from '../../components/PageHeader';
import { PermissionDenied } from '../../components/PermissionDenied';
import { IndividualsBioData } from '../../components/population/IndividualBioData';
import { IndividualPhotoModal } from '../../components/population/IndividualPhotoModal';
import { IndividualVulnerabilities } from '../../components/population/IndividualVunerabilities';
import { hasPermissions, PERMISSIONS } from '../../config/permissions';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { usePermissions } from '../../hooks/usePermissions';
import { isPermissionDeniedError } from '../../utils/utils';
import {
  IndividualNode,
  useIndividualQuery,
} from '../../__generated__/graphql';
import { UniversalActivityLogTable } from '../tables/UniversalActivityLogTable';

const Container = styled.div`
  padding: 20px;
  && {
    display: flex;
    flex-direction: column;
    width: 100%;
  }
`;

export function PopulationIndividualsDetailsPage(): React.ReactElement {
  const { t } = useTranslation();
  const { id } = useParams();
  const businessArea = useBusinessArea();
  const permissions = usePermissions();

  const { data, loading, error } = useIndividualQuery({
    variables: {
      id,
    },
  });

  if (loading) return <LoadingComponent />;

  if (isPermissionDeniedError(error)) return <PermissionDenied />;

  if (!data || permissions === null) return null;

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: 'Individuals',
      to: `/${businessArea}/population/individuals`,
    },
  ];

  const { individual } = data;
  return (
    <div>
      <PageHeader
        title={`${t('Individual ID')}: ${individual.unicefId}`}
        breadCrumbs={
          hasPermissions(
            PERMISSIONS.POPULATION_VIEW_INDIVIDUALS_LIST,
            permissions,
          )
            ? breadCrumbsItems
            : null
        }
        possibleMatch={individual.sanctionListPossibleMatch}
        confirmedMatch={individual.sanctionListConfirmedMatch}
        withTriangle={individual.deduplicationGoldenRecordStatus !== 'UNIQUE'}
      >
        {individual.photo ? (
          <IndividualPhotoModal individual={individual as IndividualNode} />
        ) : null}
      </PageHeader>
      <Container>
        <IndividualsBioData individual={individual as IndividualNode} />
        <IndividualVulnerabilities individual={individual as IndividualNode} />
        {hasPermissions(PERMISSIONS.ACTIVITY_LOG_VIEW, permissions) && (
          <UniversalActivityLogTable objectId={individual.id} />
        )}
      </Container>
    </div>
  );
}
