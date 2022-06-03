import React, { useState } from 'react';
import get from 'lodash/get';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Button, IconButton } from '@material-ui/core';
import { Info } from '@material-ui/icons';
import { useDebounce } from '../../../hooks/useDebounce';
import { PageHeader } from '../../../components/core/PageHeader';
import { TargetPopulationFilters } from '../../../components/targeting/TargetPopulationFilters';
import { TargetPopulationTable } from '../../tables/targeting/TargetPopulationTable';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { TargetingInfoDialog } from '../../dialogs/targetPopulation/TargetingInfoDialog';
import {
  ProgramNode,
  useAllProgramsForChoicesQuery,
} from '../../../__generated__/graphql';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { usePermissions } from '../../../hooks/usePermissions';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { PermissionDenied } from '../../../components/core/PermissionDenied';

export function TargetPopulationsPage(): React.ReactElement {
  const { t } = useTranslation();
  const businessArea = useBusinessArea();
  const permissions = usePermissions();
  const [filter, setFilter] = useState({
    numIndividuals: {
      min: undefined,
      max: undefined,
    },
    name: '',
    status: '',
  });
  const [isInfoOpen, setToggleInfo] = useState(false);
  const debouncedFilter = useDebounce(filter, 500);
  const { data, loading } = useAllProgramsForChoicesQuery({
    variables: { businessArea },
    fetchPolicy: 'cache-and-network',
  });

  if (loading) return <LoadingComponent />;
  if (permissions === null) return null;

  const canCreate = hasPermissions(PERMISSIONS.TARGETING_CREATE, permissions);

  if (!hasPermissions(PERMISSIONS.TARGETING_VIEW_LIST, permissions))
    return <PermissionDenied />;

  const allPrograms = get(data, 'allPrograms.edges', []);
  const programs = allPrograms.map((edge) => edge.node);

  return (
    <>
      <PageHeader title={t('Targeting')}>
        <>
          <IconButton
            onClick={() => setToggleInfo(true)}
            color='primary'
            aria-label='Targeting Information'
          >
            <Info />
          </IconButton>
          <TargetingInfoDialog open={isInfoOpen} setOpen={setToggleInfo} />
          {canCreate && (
            <Button
              variant='contained'
              color='primary'
              component={Link}
              to={`/${businessArea}/target-population/create`}
              data-cy='button-target-population-create-new'
            >
              Create new
            </Button>
          )}
        </>
      </PageHeader>
      <TargetPopulationFilters
        filter={filter}
        programs={programs as ProgramNode[]}
        onFilterChange={setFilter}
      />
      <TargetPopulationTable
        filter={debouncedFilter}
        canViewDetails={hasPermissions(
          PERMISSIONS.TARGETING_VIEW_DETAILS,
          permissions,
        )}
      />
    </>
  );
}
