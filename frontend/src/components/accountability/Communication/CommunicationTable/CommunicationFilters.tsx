import { Grid, MenuItem } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { useHistory, useLocation } from 'react-router-dom';
import {
  useAllProgramsForChoicesQuery,
  useAllTargetPopulationForChoicesQuery,
} from '../../../../__generated__/graphql';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { AssigneeAutocomplete } from '../../../../shared/autocompletes/AssigneeAutocomplete';
import {
  createHandleApplyFilterChange,
  dateToIsoString,
} from '../../../../utils/utils';
import { ClearApplyButtons } from '../../../core/ClearApplyButtons';
import { ContainerWithBorder } from '../../../core/ContainerWithBorder';
import { DatePickerFilter } from '../../../core/DatePickerFilter';
import { LoadingComponent } from '../../../core/LoadingComponent';
import { SelectFilter } from '../../../core/SelectFilter';
import { TargetPopulationAutocomplete } from '../../../../shared/autocompletes/TargetPopulationAutocomplete';

interface CommunicationFiltersProps {
  filter;
  setFilter: (filter) => void;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
}
export const CommunicationFilters = ({
  filter,
  setFilter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
}: CommunicationFiltersProps): React.ReactElement => {
  const { t } = useTranslation();
  const history = useHistory();
  const location = useLocation();

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

  const businessArea = useBusinessArea();
  const { data, loading: programsLoading } = useAllProgramsForChoicesQuery({
    variables: { businessArea },
    fetchPolicy: 'cache-and-network',
  });

  const {
    data: allTargetPopulationForChoices,
    loading: targetPopulationsLoading,
  } = useAllTargetPopulationForChoicesQuery({
    variables: { businessArea },
    fetchPolicy: 'cache-and-network',
  });

  const allPrograms = data?.allPrograms?.edges || [];
  const programs = allPrograms.map((edge) => edge.node);

  const allTargetPopulations =
    allTargetPopulationForChoices?.allTargetPopulation?.edges || [];
  const targetPopulations = allTargetPopulations.map((edge) => edge.node);

  if (programsLoading || targetPopulationsLoading) return <LoadingComponent />;

  return (
    <ContainerWithBorder>
      <Grid container alignItems='flex-end' spacing={3}>
        <Grid item xs={5}>
          <SelectFilter
            onChange={(e) => handleFilterChange('program', e.target.value)}
            label={t('Programme')}
            value={filter.program}
          >
            {programs.map((program) => (
              <MenuItem key={program.id} value={program.id}>
                {program.name}
              </MenuItem>
            ))}
          </SelectFilter>
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
        <Grid item xs={3}>
          <AssigneeAutocomplete
            label='User'
            filter={filter}
            name='userId'
            value={filter.userId}
            setFilter={setFilter}
            initialFilter={initialFilter}
            appliedFilter={appliedFilter}
            setAppliedFilter={setAppliedFilter}
          />
        </Grid>
        <Grid container item xs={6} spacing={3} alignItems='flex-end'>
          <Grid item xs={6}>
            <DatePickerFilter
              topLabel={t('Creation Date')}
              label='From'
              onChange={(date) =>
                handleFilterChange(
                  'createdAtRangeMin',
                  dateToIsoString(date, 'startOfDay'),
                )
              }
              value={filter.createdAtRangeMin}
            />
          </Grid>
          <Grid item xs={6}>
            <DatePickerFilter
              label={t('To')}
              onChange={(date) =>
                handleFilterChange(
                  'createdAtRangeMax',
                  dateToIsoString(date, 'endOfDay'),
                )
              }
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
