import { Grid, MenuItem } from '@material-ui/core';
import CakeIcon from '@material-ui/icons/Cake';
import FlashOnIcon from '@material-ui/icons/FlashOn';
import WcIcon from '@material-ui/icons/Wc';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { useHistory, useLocation } from 'react-router-dom';
import {
  IndividualChoiceDataQuery,
  ProgramNode,
} from '../../__generated__/graphql';
import { useBaseUrl } from '../../hooks/useBaseUrl';
import { AdminAreaAutocomplete } from '../../shared/autocompletes/AdminAreaAutocomplete';
import { individualTableOrderOptions } from '../../utils/constants';
import { createHandleApplyFilterChange } from '../../utils/utils';
import { DatePickerFilter } from '../core/DatePickerFilter';
import { FiltersSection } from '../core/FiltersSection';
import { NumberTextField } from '../core/NumberTextField';
import { SearchTextField } from '../core/SearchTextField';
import { SelectFilter } from '../core/SelectFilter';

interface IndividualsFilterProps {
  filter;
  programs?: ProgramNode[];
  choicesData: IndividualChoiceDataQuery;
  setFilter: (filter) => void;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
  isOnPaper?: boolean;
}

export const IndividualsFilter = ({
  filter,
  programs,
  choicesData,
  setFilter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
  isOnPaper = true,
}: IndividualsFilterProps): React.ReactElement => {
  const { t } = useTranslation();
  const history = useHistory();
  const location = useLocation();
  const { isAllPrograms } = useBaseUrl();

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
    <FiltersSection
      clearHandler={handleClearFilter}
      applyHandler={handleApplyFilter}
      isOnPaper={isOnPaper}
    >
      <Grid container alignItems='flex-end' spacing={3}>
        <Grid container item xs={6} spacing={0}>
          <Grid item xs={8}>
            <SearchTextField
              label={t('Search')}
              value={filter.search}
              onChange={(e) => handleFilterChange('search', e.target.value)}
              data-cy='ind-filters-search'
            />
          </Grid>
          <Grid item xs={4}>
            <SelectFilter
              onChange={(e) => handleFilterChange('searchType', e.target.value)}
              label={t('Search Type')}
              value={filter.searchType}
              borderRadius='0px 4px 4px 0px'
              data-cy='filter-search-type'
              fullWidth
              disableClearable
            >
              {choicesData?.individualSearchTypesChoices.map(
                ({ name, value }) => (
                  <MenuItem key={value} value={value}>
                    {name}
                  </MenuItem>
                ),
              )}
            </SelectFilter>
          </Grid>
        </Grid>
        {isAllPrograms && (
          <Grid item xs={3}>
            <SelectFilter
              onChange={(e) => handleFilterChange('program', e.target.value)}
              label={t('Programme')}
              value={filter.program}
              fullWidth
              icon={<FlashOnIcon />}
              data-cy='filters-program'
            >
              {programs.map((program) => (
                <MenuItem key={program.id} value={program.id}>
                  {program.name}
                </MenuItem>
              ))}
            </SelectFilter>
          </Grid>
        )}
        <Grid item xs={3}>
          <AdminAreaAutocomplete
            name='admin2'
            value={filter.admin2}
            setFilter={setFilter}
            filter={filter}
            initialFilter={initialFilter}
            appliedFilter={appliedFilter}
            setAppliedFilter={setAppliedFilter}
            dataCy='ind-filters-admin2'
          />
        </Grid>
        <Grid item xs={3}>
          <SelectFilter
            onChange={(e) => handleFilterChange('sex', e.target.value)}
            value={filter.sex}
            label={t('Gender')}
            icon={<WcIcon />}
            data-cy='ind-filters-gender'
            fullWidth
          >
            <MenuItem value='FEMALE'>{t('Female')}</MenuItem>
            <MenuItem value='MALE'>{t('Male')}</MenuItem>
          </SelectFilter>
        </Grid>
        <Grid item xs={3}>
          <NumberTextField
            fullWidth
            topLabel={t('Age')}
            placeholder={t('From')}
            value={filter.ageMin}
            data-cy='ind-filters-age-from'
            onChange={(e) => {
              if (e.target.value < 0 || e.target.value > 120) return;
              handleFilterChange('ageMin', e.target.value);
            }}
            icon={<CakeIcon />}
          />
        </Grid>
        <Grid item xs={3}>
          <NumberTextField
            fullWidth
            placeholder={t('To')}
            value={filter.ageMax}
            data-cy='ind-filters-age-to'
            onChange={(e) => {
              if (e.target.value < 0 || e.target.value > 120) return;
              handleFilterChange('ageMax', e.target.value);
            }}
            icon={<CakeIcon />}
          />
        </Grid>
        <Grid item xs={3}>
          <SelectFilter
            onChange={(e) => handleFilterChange('flags', e.target.value)}
            label={t('Flags')}
            multiple
            fullWidth
            value={filter.flags}
            data-cy='ind-filters-flags'
          >
            {choicesData?.flagChoices.map((each, index) => (
              <MenuItem
                key={each.value}
                value={each.value}
                data-cy={`select-option-${index}`}
              >
                {each.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </Grid>
        <Grid item xs={3}>
          <SelectFilter
            onChange={(e) => handleFilterChange('orderBy', e.target.value)}
            label={t('Sort by')}
            value={filter.orderBy}
            fullWidth
            data-cy='ind-filters-order-by'
            disableClearable
          >
            {individualTableOrderOptions.map((order) => (
              <MenuItem key={order.value} value={order.value}>
                {order.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </Grid>
        <Grid item xs={3}>
          <SelectFilter
            onChange={(e) => handleFilterChange('status', e.target.value)}
            label={t('Status')}
            value={filter.status}
            data-cy='ind-filters-status'
          >
            <MenuItem key='active' value='ACTIVE'>
              Active
            </MenuItem>
            <MenuItem key='duplicate' value='DUPLICATE'>
              Duplicate
            </MenuItem>
            <MenuItem key='withdrawn' value='WITHDRAWN'>
              Withdrawn
            </MenuItem>
          </SelectFilter>
        </Grid>
        <Grid item xs={3}>
          <DatePickerFilter
            topLabel={t('Registration Date')}
            placeholder={t('From')}
            onChange={(date) =>
              handleFilterChange('lastRegistrationDateMin', date)
            }
            value={filter.lastRegistrationDateMin}
            data-cy='ind-filters-reg-date-from'
          />
        </Grid>
        <Grid item xs={3}>
          <DatePickerFilter
            placeholder={t('To')}
            onChange={(date) =>
              handleFilterChange('lastRegistrationDateMax', date)
            }
            value={filter.lastRegistrationDateMax}
            data-cy='ind-filters-reg-date-to'
          />
        </Grid>
        {isAllPrograms && (
          <Grid item xs={3}>
            <SelectFilter
              onChange={(e) =>
                handleFilterChange('programState', e.target.value)
              }
              label={t('Programme State')}
              value={filter.programState}
              fullWidth
              disableClearable
              data-cy='filters-program-state'
            >
              <MenuItem value='active'>{t('Active Programmes')}</MenuItem>
              <MenuItem value='all'>{t('All Programmes')}</MenuItem>
            </SelectFilter>
          </Grid>
        )}
      </Grid>
    </FiltersSection>
  );
};
