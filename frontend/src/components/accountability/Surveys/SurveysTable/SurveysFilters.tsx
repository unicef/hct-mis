import { Grid } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { useHistory, useLocation } from 'react-router-dom';
import { AssigneeAutocomplete } from '../../../../shared/autocompletes/AssigneeAutocomplete';
import { TargetPopulationAutocomplete } from '../../../../shared/autocompletes/TargetPopulationAutocomplete';
import { createHandleApplyFilterChange } from '../../../../utils/utils';
import { ClearApplyButtons } from '../../../core/ClearApplyButtons';
import { ContainerWithBorder } from '../../../core/ContainerWithBorder';
import { DatePickerFilter } from '../../../core/DatePickerFilter';
import { SearchTextField } from '../../../core/SearchTextField';

interface SurveysFiltersProps {
  filter;
  setFilter: (filter) => void;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
}
export const SurveysFilters = ({
  filter,
  setFilter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
}: SurveysFiltersProps): React.ReactElement => {
  const history = useHistory();
  const location = useLocation();
  const { t } = useTranslation();
  const {
    handleFilterChange,
    applyFilterChanges,
    clearFilter,
  } = createHandleApplyFilterChange(
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
    <ContainerWithBorder>
      <Grid container alignItems='center' spacing={3}>
        <Grid xs={3} item>
          <SearchTextField
            value={filter.search}
            label='Search'
            onChange={(e) => handleFilterChange('search', e.target.value)}
            data-cy='filters-search'
            fullWidth
          />
        </Grid>
        <Grid xs={4} item>
          <TargetPopulationAutocomplete
            name='targetPopulation'
            value={filter.targetPopulation}
            filter={filter}
            setFilter={setFilter}
            initialFilter={initialFilter}
            appliedFilter={appliedFilter}
            setAppliedFilter={setAppliedFilter}
          />
        </Grid>
        <Grid container item xs={12} spacing={3} alignItems='flex-end'>
          <Grid item xs={4}>
            <AssigneeAutocomplete
              name='createdBy'
              label={t('Created by')}
              value={filter.createdBy}
              filter={filter}
              setFilter={setFilter}
              initialFilter={initialFilter}
              appliedFilter={appliedFilter}
              setAppliedFilter={setAppliedFilter}
            />
          </Grid>
          <Grid item xs={4}>
            <DatePickerFilter
              topLabel={t('Creation Date')}
              label='From'
              onChange={(date) => handleFilterChange('createdAtRangeMin', date)}
              value={filter.createdAtRangeMin}
            />
          </Grid>
          <Grid item xs={4}>
            <DatePickerFilter
              label={t('To')}
              onChange={(date) => handleFilterChange('createdAtRangeMax', date)}
              value={filter.createdAtRangeMax}
            />
          </Grid>
        </Grid>
      </Grid>
      <ClearApplyButtons
        clearHandler={handleClearFilter}
        applyHandler={handleApplyFilter}
      />
    </ContainerWithBorder>
  );
};
