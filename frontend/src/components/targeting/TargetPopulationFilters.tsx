import { Grid, MenuItem } from '@material-ui/core';
import { Group, Person } from '@material-ui/icons';
import FlashOnIcon from '@material-ui/icons/FlashOn';
import moment from 'moment';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { useHistory, useLocation } from 'react-router-dom';
import {
  ProgramNode,
  TargetPopulationStatus,
} from '../../__generated__/graphql';
import {
  createHandleApplyFilterChange,
  dateToIsoString,
  targetPopulationStatusMapping,
} from '../../utils/utils';
import { ClearApplyButtons } from '../core/ClearApplyButtons';
import { ContainerWithBorder } from '../core/ContainerWithBorder';
import { DatePickerFilter } from '../core/DatePickerFilter';
import { NumberTextField } from '../core/NumberTextField';
import { SearchTextField } from '../core/SearchTextField';
import { SelectFilter } from '../core/SelectFilter';

interface TargetPopulationFiltersProps {
  filter;
  programs: ProgramNode[];
  addBorder?: boolean;
  setFilter: (filter) => void;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
}
export const TargetPopulationFilters = ({
  filter,
  programs,
  addBorder = true,
  setFilter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
}: TargetPopulationFiltersProps): React.ReactElement => {
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

  const renderTable = (): React.ReactElement => (
    <>
      <Grid container alignItems='flex-end' spacing={3}>
        <Grid item xs={3}>
          <SearchTextField
            label={t('Search')}
            value={filter.name}
            onChange={(e) => handleFilterChange('name', e.target.value)}
            data-cy='filters-search'
            fullWidth
          />
        </Grid>
        <Grid item xs={3}>
          <SelectFilter
            onChange={(e) => handleFilterChange('status', e.target.value)}
            value={filter.status}
            label={t('Status')}
            icon={<Person />}
            fullWidth
            data-cy='filters-status'
          >
            {Object.values(TargetPopulationStatus)
              .sort()
              .map((key) => (
                <MenuItem key={key} value={key}>
                  {targetPopulationStatusMapping(key)}
                </MenuItem>
              ))}
          </SelectFilter>
        </Grid>
        <Grid item xs={3}>
          <SelectFilter
            onChange={(e) => handleFilterChange('program', e.target.value)}
            label={t('Programme')}
            value={filter.program}
            icon={<FlashOnIcon />}
            fullWidth
            data-cy='filters-program'
          >
            {programs.map((program) => (
              <MenuItem key={program.id} value={program.id}>
                {program.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </Grid>
        <Grid item xs={3}>
          <NumberTextField
            topLabel={t('Number of Households')}
            value={filter.totalHouseholdsCountMin}
            placeholder={t('From')}
            onChange={(e) =>
              handleFilterChange('totalHouseholdsCountMin', e.target.value)
            }
            icon={<Group />}
            data-cy='filters-total-households-count-min'
          />
        </Grid>
        <Grid item xs={3}>
          <NumberTextField
            value={filter.totalHouseholdsCountMax}
            placeholder={t('To')}
            onChange={(e) =>
              handleFilterChange('totalHouseholdsCountMax', e.target.value)
            }
            icon={<Group />}
            data-cy='filters-total-households-count-max'
          />
        </Grid>
        <Grid item xs={3}>
          <DatePickerFilter
            topLabel={t('Date Created')}
            placeholder={t('From')}
            onChange={(date) =>
              handleFilterChange(
                'createdAtRangeMin',
                dateToIsoString(date, 'startOfDay'),
              )
            }
            value={filter.createdAtRangeMin}
          />
        </Grid>
        <Grid item xs={3}>
          <DatePickerFilter
            placeholder={t('To')}
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
      <ClearApplyButtons
        applyHandler={handleApplyFilter}
        clearHandler={handleClearFilter}
      />
    </>
  );

  return addBorder ? (
    <ContainerWithBorder>{renderTable()}</ContainerWithBorder>
  ) : (
    renderTable()
  );
};
