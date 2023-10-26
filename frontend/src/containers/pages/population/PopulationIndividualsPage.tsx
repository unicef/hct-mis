import { Box } from '@material-ui/core';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import {
  useHouseholdChoiceDataQuery,
  useIndividualChoiceDataQuery,
} from '../../../__generated__/graphql';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PageHeader } from '../../../components/core/PageHeader';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { IndividualsFilter } from '../../../components/population/IndividualsFilter';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { useBaseUrl } from '../../../hooks/useBaseUrl';
import { usePermissions } from '../../../hooks/usePermissions';
import { getFilterFromQueryParams } from '../../../utils/utils';
import { IndividualsListTable } from '../../tables/population/IndividualsListTable';

const initialFilter = {
  search: '',
  searchType: 'individual_id',
  admin2: '',
  sex: '',
  ageMin: '',
  ageMax: '',
  flags: [],
  orderBy: 'unicef_id',
  status: '',
  lastRegistrationDateMin: '',
  lastRegistrationDateMax: '',
};

export const PopulationIndividualsPage = (): React.ReactElement => {
  const { t } = useTranslation();
  const location = useLocation();
  const { businessArea } = useBaseUrl();
  const permissions = usePermissions();
  const {
    data: householdChoicesData,
    loading: householdChoicesLoading,
  } = useHouseholdChoiceDataQuery();

  const [filter, setFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const [appliedFilter, setAppliedFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );

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
        choicesData={individualChoicesData}
        setFilter={setFilter}
        initialFilter={initialFilter}
        appliedFilter={appliedFilter}
        setAppliedFilter={setAppliedFilter}
      />
      <Box
        display='flex'
        flexDirection='column'
        data-cy='page-details-container'
      >
        <IndividualsListTable
          filter={appliedFilter}
          businessArea={businessArea}
          choicesData={householdChoicesData}
          canViewDetails={hasPermissions(
            PERMISSIONS.POPULATION_VIEW_INDIVIDUALS_DETAILS,
            permissions,
          )}
        />
      </Box>
    </>
  );
};
