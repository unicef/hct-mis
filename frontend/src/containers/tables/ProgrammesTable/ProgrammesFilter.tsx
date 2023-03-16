import { Grid, MenuItem, Paper } from '@material-ui/core';
import { useHistory, useLocation } from 'react-router-dom';
import GroupIcon from '@material-ui/icons/Group';
import moment from 'moment';
import React from 'react';
import { DatePickerFilter } from '../../../components/core/DatePickerFilter';
import { NumberTextField } from '../../../components/core/NumberTextField';
import { SearchTextField } from '../../../components/core/SearchTextField';
import { SelectFilter } from '../../../components/core/SelectFilter';
import { ProgrammeChoiceDataQuery } from '../../../__generated__/graphql';
import { createHandleFilterChange } from '../../../utils/utils';

interface ProgrammesFilterProps {
  onFilterChange;
  filter;
  choicesData: ProgrammeChoiceDataQuery;
}
export const ProgrammesFilters = ({
  onFilterChange,
  filter,
  choicesData,
}: ProgrammesFilterProps): React.ReactElement => {
  const history = useHistory();
  const location = useLocation();

  const handleFilterChange = createHandleFilterChange(
    onFilterChange,
    filter,
    history,
    location,
  );

  return (
    <Grid container alignItems='center' spacing={3}>
      <Grid container alignItems='center' spacing={3}>
        <Grid item xs={12}>
          <Grid container alignItems='center' spacing={3}>
            <Grid item>
              <SearchTextField
                label='Search'
                value={filter.search}
                onChange={(e) => handleFilterChange('search', e.target.value)}
                data-cy='filters-search'
              />
            </Grid>
            <Grid item>
              <SelectFilter
                onChange={(e) => handleFilterChange('status', e.target.value)}
                label='Status'
                value={filter.status}
              >
                <MenuItem value=''>
                  <em>None</em>
                </MenuItem>
                {choicesData.programStatusChoices.map((item) => {
                  return (
                    <MenuItem key={item.value} value={item.value}>
                      {item.name}
                    </MenuItem>
                  );
                })}
              </SelectFilter>
            </Grid>
            <Grid item>
              <DatePickerFilter
                label='Start Date'
                onChange={(date) =>
                  handleFilterChange(
                    'startDate',
                    moment(date).format('YYYY-MM-DD'),
                  )
                }
                value={filter.startDate}
              />
            </Grid>
            <Grid item>
              <DatePickerFilter
                label='End Date'
                onChange={(date) =>
                  handleFilterChange(
                    'endDate',
                    moment(date).format('YYYY-MM-DD'),
                  )
                }
                value={filter.endDate}
              />
            </Grid>
            <Grid item>
              <SelectFilter
                onChange={(e) => handleFilterChange('sector', e.target.value)}
                label='Sector'
                value={filter.sector}
                multiple
              >
                <MenuItem value=''>
                  <em>None</em>
                </MenuItem>
                {choicesData.programSectorChoices.map((item) => {
                  return (
                    <MenuItem key={item.value} value={item.value}>
                      {item.name}
                    </MenuItem>
                  );
                })}
              </SelectFilter>
            </Grid>
          </Grid>
        </Grid>
        <Grid item xs={12}>
          <Grid container alignItems='flex-end' spacing={3}>
            <Grid item>
              <NumberTextField
                topLabel='Num. of Households'
                placeholder='From'
                value={filter.numberOfHouseholdsMin}
                onChange={(e) =>
                  handleFilterChange('numberOfHouseholdsMin', e.target.value)
                }
                icon={<GroupIcon />}
              />
            </Grid>
            <Grid item>
              <NumberTextField
                value={filter.numberOfHouseholdsMax}
                placeholder='To'
                onChange={(e) =>
                  handleFilterChange('numberOfHouseholdsMax', e.target.value)
                }
                icon={<GroupIcon />}
              />
            </Grid>
            <Grid item>
              <NumberTextField
                topLabel='Budget (USD)'
                value={filter.budgetMin}
                placeholder='From'
                onChange={(e) =>
                  handleFilterChange('budgetMin', e.target.value)
                }
              />
            </Grid>
            <Grid item>
              <NumberTextField
                value={filter.budgetMax}
                placeholder='To'
                onChange={(e) =>
                  handleFilterChange('budgetMax', e.target.value)
                }
              />
            </Grid>
          </Grid>
        </Grid>
      </Grid>
    </Grid>
  );
};
