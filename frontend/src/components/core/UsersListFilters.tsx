import { Grid, MenuItem } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { useUserChoiceDataQuery } from '../../__generated__/graphql';
import { ContainerWithBorder } from './ContainerWithBorder';
import { SearchTextField } from './SearchTextField';
import { SelectFilter } from './SelectFilter';

interface UsersListFiltersProps {
  onFilterChange;
  filter;
}
export function UsersListFilters({
  onFilterChange,
  filter,
}: UsersListFiltersProps): React.ReactElement {
  const { t } = useTranslation();
  const handleFilterChange = (e, name): void =>
    onFilterChange({ ...filter, [name]: e.target.value });
  const { data: choices } = useUserChoiceDataQuery();
  if (!choices) {
    return null;
  }

  return (
    <ContainerWithBorder>
      <Grid container spacing={3}>
        <Grid item>
          <SearchTextField
            label={t('Search')}
            value={filter.search}
            onChange={(e) => handleFilterChange(e, 'search')}
          />
        </Grid>
        <Grid item>
          <SelectFilter
            onChange={(e) => handleFilterChange(e, 'partner')}
            label={t('Partner')}
            value={filter.partner}
          >
            <MenuItem value=''>
              <em>{t('None')}</em>
            </MenuItem>
            {choices.userPartnerChoices.map((item) => {
              return (
                <MenuItem key={item.value} value={item.value}>
                  {item.name}
                </MenuItem>
              );
            })}
          </SelectFilter>
        </Grid>
        <Grid item>
          <SelectFilter
            onChange={(e) => handleFilterChange(e, 'roles')}
            label={t('Role')}
            value={filter.roles}
          >
            <MenuItem value=''>
              <em>{t('None')}</em>
            </MenuItem>
            {choices.userRolesChoices.map((item) => {
              return (
                <MenuItem key={item.value} value={item.value}>
                  {item.name}
                </MenuItem>
              );
            })}
          </SelectFilter>
        </Grid>
        <Grid item>
          <SelectFilter
            onChange={(e) => handleFilterChange(e, 'status')}
            label={t('Status')}
            value={filter.status}
          >
            <MenuItem value=''>
              <em>{t('None')}</em>
            </MenuItem>
            {choices.userStatusChoices.map((item) => {
              return (
                <MenuItem key={item.value} value={item.value}>
                  {item.name}
                </MenuItem>
              );
            })}
          </SelectFilter>
        </Grid>
      </Grid>
    </ContainerWithBorder>
  );
}
