import { Button, Grid, MenuItem } from '@material-ui/core';
import FlashOnIcon from '@material-ui/icons/FlashOn';
import GroupIcon from '@material-ui/icons/Group';
import moment from 'moment';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { LookUpAdminAreaAutocomplete } from '../../../../shared/autocompletes/LookUpAdminAreaAutocomplete';
import {
  HouseholdChoiceDataQuery,
  ProgramNode,
} from '../../../../__generated__/graphql';
import { ContainerWithBorder } from '../../../core/ContainerWithBorder';
import { DatePickerFilter } from '../../../core/DatePickerFilter';
import { NumberTextField } from '../../../core/NumberTextField';
import { SearchTextField } from '../../../core/SearchTextField';
import { SelectFilter } from '../../../core/SelectFilter';

interface LookUpHouseholdFiltersProps {
  onFilterChange;
  filter;
  programs: ProgramNode[];
  choicesData: HouseholdChoiceDataQuery;
  setFilterHouseholdApplied?;
  householdFilterInitial?;
  addBorder?: boolean;
}
export function LookUpHouseholdFilters({
  onFilterChange,
  filter,
  programs,
  choicesData,
  setFilterHouseholdApplied,
  householdFilterInitial,
  addBorder = true,
}: LookUpHouseholdFiltersProps): React.ReactElement {
  const { t } = useTranslation();
  const handleFilterChange = (e, name): void =>
    onFilterChange({ ...filter, [name]: e.target.value });

  const renderTable = (): React.ReactElement => {
    return (
      <Grid container alignItems='flex-end' spacing={3}>
        <Grid item xs={3}>
          <SearchTextField
            label={t('Search')}
            value={filter.search}
            onChange={(e) => handleFilterChange(e, 'search')}
            data-cy='filters-search'
            fullWidth
          />
        </Grid>
        <Grid item xs={3}>
          <SelectFilter
            onChange={(e) => handleFilterChange(e, 'programs')}
            label={t('Programme')}
            value={filter.programs || []}
            icon={<FlashOnIcon />}
            fullWidth
          >
            {programs.map((program) => (
              <MenuItem key={program.id} value={program.id}>
                {program.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </Grid>
        <Grid item xs={3}>
          <DatePickerFilter
            topLabel={t('Registration Date')}
            placeholder={t('From')}
            onChange={(date) =>
              onFilterChange({
                ...filter,
                lastRegistrationDate: {
                  ...filter.lastRegistrationDate,
                  min: date ? moment(date).format('YYYY-MM-DD') : undefined,
                },
              })
            }
            value={filter.lastRegistrationDate.min}
          />
        </Grid>
        <Grid item xs={3}>
          <DatePickerFilter
            placeholder={t('To')}
            onChange={(date) =>
              onFilterChange({
                ...filter,
                lastRegistrationDate: {
                  ...filter.lastRegistrationDate,
                  max: date ? moment(date).format('YYYY-MM-DD') : undefined,
                },
              })
            }
            value={filter.lastRegistrationDate.max}
          />
        </Grid>
        <Grid item xs={3}>
          <SelectFilter
            onChange={(e) => handleFilterChange(e, 'residenceStatus')}
            label={t('Status')}
            value={filter.residenceStatus}
            fullWidth
          >
            {choicesData.residenceStatusChoices?.map((item) => {
              return (
                <MenuItem key={item.value} value={item.value}>
                  {item.name}
                </MenuItem>
              );
            })}
          </SelectFilter>
        </Grid>
        <Grid item xs={3}>
          <LookUpAdminAreaAutocomplete
            onFilterChange={onFilterChange}
            name='admin2'
            value={filter.admin2}
            fullWidth
          />
        </Grid>
        <Grid item xs={3}>
          <NumberTextField
            topLabel={t('Household Size')}
            value={filter.size.min}
            placeholder='From'
            icon={<GroupIcon />}
            onChange={(e) =>
              onFilterChange({
                ...filter,
                size: {
                  ...filter.size,
                  min: e.target.value,
                },
              })
            }
          />
        </Grid>
        <Grid item xs={3}>
          <NumberTextField
            value={filter.size.max}
            placeholder='To'
            icon={<GroupIcon />}
            onChange={(e) =>
              onFilterChange({
                ...filter,
                size: {
                  ...filter.size,
                  max: e.target.value,
                },
              })
            }
          />
        </Grid>
        {householdFilterInitial && (
          <Grid container justifyContent='flex-end'>
            <Button
              color='primary'
              onClick={() => {
                setFilterHouseholdApplied(householdFilterInitial);
                onFilterChange(householdFilterInitial);
              }}
            >
              {t('Clear')}
            </Button>
            <Button
              color='primary'
              variant='outlined'
              onClick={() => setFilterHouseholdApplied(filter)}
            >
              {t('Apply')}
            </Button>
          </Grid>
        )}
      </Grid>
    );
  };
  return addBorder ? (
    <ContainerWithBorder>{renderTable()}</ContainerWithBorder>
  ) : (
    renderTable()
  );
}
