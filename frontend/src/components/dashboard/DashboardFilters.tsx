import { Grid } from '@material-ui/core';
import React from 'react';
import { useHistory, useLocation } from 'react-router-dom';
import { useBaseUrl } from '../../hooks/useBaseUrl';
import { AdminAreaAutocomplete } from '../../shared/autocompletes/AdminAreaAutocomplete';
import { createHandleApplyFilterChange } from '../../utils/utils';
import { FiltersSection } from '../core/FiltersSection';
import { ProgramAutocomplete } from '../../shared/autocompletes/ProgramAutocomplete';

interface DashboardFiltersProps {
  filter;
  setFilter;
  initialFilter;
  appliedFilter;
  setAppliedFilter;
}

export const DashboardFilters = ({
  filter,
  setFilter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
}: DashboardFiltersProps): React.ReactElement => {
  const history = useHistory();
  const location = useLocation();
  const { isAllPrograms } = useBaseUrl();

  const { applyFilterChanges, clearFilter } = createHandleApplyFilterChange(
    initialFilter,
    history,
    location,
    filter,
    setFilter,
    appliedFilter,
    setAppliedFilter,
  );
  const handleApplyFilter = (): void => {
    applyFilterChanges();
  };

  const handleClearFilter = (): void => {
    clearFilter();
  };

  return (
    <FiltersSection
      clearHandler={handleClearFilter}
      applyHandler={handleApplyFilter}
    >
      <Grid container alignItems='flex-end' spacing={3}>
        {isAllPrograms && (
          <Grid item xs={5}>
            <ProgramAutocomplete
              filter={filter}
              name='program'
              value={filter.program}
              setFilter={setFilter}
              initialFilter={initialFilter}
              appliedFilter={appliedFilter}
              setAppliedFilter={setAppliedFilter}
            />
          </Grid>
        )}
        <Grid item xs={3}>
          <AdminAreaAutocomplete
            name='administrativeArea'
            value={filter.administrativeArea}
            filter={filter}
            setFilter={setFilter}
            initialFilter={initialFilter}
            appliedFilter={appliedFilter}
            setAppliedFilter={setAppliedFilter}
            dataCy='filter-administrative-area'
          />
        </Grid>
      </Grid>
    </FiltersSection>
  );
};
