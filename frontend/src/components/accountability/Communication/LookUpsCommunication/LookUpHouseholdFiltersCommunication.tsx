import { Grid, MenuItem } from '@material-ui/core';
import AssignmentIndRoundedIcon from '@material-ui/icons/AssignmentIndRounded';
import GroupIcon from '@material-ui/icons/Group';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { useHistory, useLocation } from 'react-router-dom';
import { HouseholdChoiceDataQuery } from '../../../../__generated__/graphql';
import { AdminAreaAutocomplete } from '../../../../shared/autocompletes/AdminAreaAutocomplete';
import { createHandleApplyFilterChange } from '../../../../utils/utils';
import { ClearApplyButtons } from '../../../core/ClearApplyButtons';
import { ContainerWithBorder } from '../../../core/ContainerWithBorder';
import { NumberTextField } from '../../../core/NumberTextField';
import { SearchTextField } from '../../../core/SearchTextField';
import { SelectFilter } from '../../../core/SelectFilter';

interface LookUpHouseholdFiltersCommunicationProps {
  filter;
  choicesData: HouseholdChoiceDataQuery;
  setFilter: (filter) => void;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
  isOnPaper?: boolean;
}

const orderOptions = [
  { name: 'Household Id: ascending', value: 'unicef_id' },
  { name: 'Household Id: descending', value: '-unicef_id' },
  { name: 'Status: ascending', value: 'status_label' },
  { name: 'Status: descending', value: '-status_label' },
  { name: 'Household Size: ascending', value: 'size' },
  { name: 'Household Size: descending', value: '-size' },
];
export const LookUpHouseholdFiltersCommunication = ({
  filter,
  choicesData,
  setFilter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
  isOnPaper = true,
}: LookUpHouseholdFiltersCommunicationProps): React.ReactElement => {
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

  const filtersComponent = (
    <>
      <Grid container alignItems='flex-end' spacing={3}>
        <Grid item xs={3}>
          <SearchTextField
            label={t('Search')}
            value={filter.search}
            fullWidth
            onChange={(e) => handleFilterChange('search', e.target.value)}
            data-cy='hh-filters-search'
          />
        </Grid>
        <Grid item xs={3}>
          <SelectFilter
            onChange={(e) =>
              handleFilterChange('residenceStatus', e.target.value)
            }
            label={t('Residence Status')}
            fullWidth
            value={filter.residenceStatus}
            icon={<AssignmentIndRoundedIcon />}
            data-cy='hh-filters-residence-status'
          >
            {choicesData.residenceStatusChoices?.map((status) => (
              <MenuItem key={status.value} value={status.value}>
                {status.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </Grid>
        <Grid item xs={3}>
          <AdminAreaAutocomplete
            name='admin2'
            value={filter.admin2}
            filter={filter}
            setFilter={setFilter}
            initialFilter={initialFilter}
            appliedFilter={appliedFilter}
            setAppliedFilter={setAppliedFilter}
            data-cy='hh-filters-admin2'
          />
        </Grid>
        <Grid item xs={3}>
          <NumberTextField
            topLabel={t('Household Size')}
            value={filter.householdSizeMin}
            placeholder={t('From')}
            icon={<GroupIcon />}
            fullWidth
            onChange={(e) =>
              handleFilterChange('householdSizeMin', e.target.value)
            }
            data-cy='hh-filters-household-size-from'
          />
        </Grid>
        <Grid item xs={3}>
          <NumberTextField
            value={filter.householdSizeMax}
            placeholder={t('To')}
            icon={<GroupIcon />}
            fullWidth
            onChange={(e) =>
              handleFilterChange('householdSizeMax', e.target.value)
            }
            data-cy='hh-filters-household-size-to'
          />
        </Grid>
        <Grid item xs={3}>
          <SelectFilter
            onChange={(e) => handleFilterChange('orderBy', e.target.value)}
            label={t('Sort by')}
            value={filter.orderBy}
            data-cy='hh-filters-order-by'
          >
            {orderOptions.map((order) => (
              <MenuItem key={order.value} value={order.value}>
                {order.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </Grid>
        <Grid item xs={3}>
          <SelectFilter
            onChange={(e) => handleFilterChange('withdrawn', e.target.value)}
            label={t('Status')}
            value={filter.withdrawn}
            data-cy='hh-filters-status'
          >
            <MenuItem key='all' value='null'>
              All
            </MenuItem>
            <MenuItem key='active' value='false'>
              Active
            </MenuItem>
            <MenuItem key='inactive' value='true'>
              Withdrawn
            </MenuItem>
          </SelectFilter>
        </Grid>
      </Grid>
      <ClearApplyButtons
        clearHandler={handleClearFilter}
        applyHandler={handleApplyFilter}
      />
    </>
  );

  return isOnPaper ? (
    <ContainerWithBorder>{filtersComponent}</ContainerWithBorder>
  ) : (
    filtersComponent
  );
};
