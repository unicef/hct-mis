import { Box } from '@material-ui/core';
import React, { useState } from 'react';
import { useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PageHeader } from '../../../components/core/PageHeader';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { IndividualsFilter } from '../../../components/population/IndividualsFilter';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { useDebounce } from '../../../hooks/useDebounce';
import { usePermissions } from '../../../hooks/usePermissions';
import { getFilterFromQueryParams } from '../../../utils/utils';
import {
  useHouseholdChoiceDataQuery,
  useIndividualChoiceDataQuery,
} from '../../../__generated__/graphql';
import { IndividualsListTable } from '../../tables/population/IndividualsListTable';

export const PopulationIndividualsPage = (): React.ReactElement => {
  const { t } = useTranslation();
  const location = useLocation();
  const businessArea = useBusinessArea();
  const permissions = usePermissions();
  const {
    data: householdChoicesData,
    loading: householdChoicesLoading,
  } = useHouseholdChoiceDataQuery();

  const initialFilter = {
    text: '',
    sex: '',
    ageMin: '',
    ageMax: '',
    flags: [],
    orderBy: 'unicef_id',
  };
  const [filter, setFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  console.log('filter in PopulationIndividualsPage', filter);

  const debouncedFilter = useDebounce(filter, 500);
  const {
    data: individualChoicesData,
    loading: individualChoicesLoading,
  } = useIndividualChoiceDataQuery();

  if (householdChoicesLoading || individualChoicesLoading)
    return <LoadingComponent />;

  if (!individualChoicesData || !householdChoicesData || permissions === null)
    return null;

  if (
    !hasPermissions(PERMISSIONS.POPULATION_VIEW_INDIVIDUALS_LIST, permissions)
  )
    return <PermissionDenied />;

  return (
    <>
      <PageHeader title={t('Individuals')} />
      <IndividualsFilter
        filter={filter}
        onFilterChange={setFilter}
        choicesData={individualChoicesData}
      />
      <Box
        display='flex'
        flexDirection='column'
        data-cy='page-details-container'
      >
        <IndividualsListTable
          filter={debouncedFilter}
          businessArea={businessArea}
          choicesData={householdChoicesData}
          canViewDetails={hasPermissions(
            PERMISSIONS.POPULATION_VIEW_INDIVIDUALS_DETAILS,
            permissions,
          )}
          filterOrderBy={filter.orderBy}
        />
      </Box>
    </>
  );
};
