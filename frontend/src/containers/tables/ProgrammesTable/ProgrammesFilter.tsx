import { Box, Grid, InputAdornment, MenuItem, Paper } from '@material-ui/core';
import GroupIcon from '@material-ui/icons/Group';
import moment from 'moment';
import React from 'react';
import styled from 'styled-components';
import { DatePickerFilter } from '../../../components/core/DatePickerFilter';
import { FieldLabel } from '../../../components/core/FieldLabel';
import { SearchTextField } from '../../../components/core/SearchTextField';
import { SelectFilter } from '../../../components/core/SelectFilter';
import TextField from '../../../shared/TextField';
import { ProgrammeChoiceDataQuery } from '../../../__generated__/graphql';

const Container = styled(Paper)`
  display: flex;
  flex: 1;
  width: 100%;
  background-color: #fff;
  padding: ${({ theme }) => theme.spacing(8)}px
    ${({ theme }) => theme.spacing(11)}px;
  flex-direction: row;
  align-items: center;
  && > div {
    margin: 5px;
  }
`;

const TextContainer = styled(TextField)`
  input[type='number']::-webkit-inner-spin-button,
  input[type='number']::-webkit-outer-spin-button {
    -webkit-appearance: none;
  }
  input[type='number'] {
    -moz-appearance: textfield;
  }
`;

interface ProgrammesFilterProps {
  onFilterChange;
  filter;
  choicesData: ProgrammeChoiceDataQuery;
}
export function ProgrammesFilters({
  onFilterChange,
  filter,
  choicesData,
}: ProgrammesFilterProps): React.ReactElement {
  const handleFilterChange = (e, name): void =>
    onFilterChange({ ...filter, [name]: e.target.value });

  return (
    <Container>
      <Grid container alignItems='center' spacing={3}>
        <Grid item xs={12}>
          <Grid container alignItems='center' spacing={3}>
            <Grid item>
              <SearchTextField
                label='Search'
                value={filter.search || ''}
                onChange={(e) => handleFilterChange(e, 'search')}
                data-cy='filters-search'
              />
            </Grid>
            <Grid item>
              <SelectFilter
                onChange={(e) => handleFilterChange(e, 'status')}
                label='Status'
                value={filter.status || null}
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
                  onFilterChange({
                    ...filter,
                    startDate: date ? moment(date).format('YYYY-MM-DD') : null,
                  })
                }
                value={filter.startDate}
              />
            </Grid>
            <Grid item>
              <DatePickerFilter
                label='End Date'
                onChange={(date) =>
                  onFilterChange({
                    ...filter,
                    endDate: date ? moment(date).format('YYYY-MM-DD') : null,
                  })
                }
                value={filter.endDate}
              />
            </Grid>
            <Grid item>
              <SelectFilter
                onChange={(e) => handleFilterChange(e, 'sector')}
                label='Sector'
                value={filter.sector || null}
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
              <Box display='flex' flexDirection='column'>
                <FieldLabel>Num. of Households</FieldLabel>
                <TextContainer
                  placeholder='From'
                  value={filter.numberOfHouseholds.min}
                  variant='outlined'
                  margin='dense'
                  onChange={(e) =>
                    onFilterChange({
                      ...filter,
                      numberOfHouseholds: {
                        ...filter.numberOfHouseholds,
                        min: e.target.value || undefined,
                      },
                    })
                  }
                  type='number'
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position='start'>
                        <GroupIcon />
                      </InputAdornment>
                    ),
                  }}
                />
              </Box>
            </Grid>
            <Grid item>
              <TextContainer
                value={filter.numberOfHouseholds.max}
                variant='outlined'
                margin='dense'
                placeholder='To'
                onChange={(e) =>
                  onFilterChange({
                    ...filter,
                    numberOfHouseholds: {
                      ...filter.numberOfHouseholds,
                      max: e.target.value || undefined,
                    },
                  })
                }
                type='number'
                InputProps={{
                  startAdornment: (
                    <InputAdornment position='start'>
                      <GroupIcon />
                    </InputAdornment>
                  ),
                }}
              />
            </Grid>
            <Grid item>
              <Box display='flex' flexDirection='column'>
                <FieldLabel>Budget (USD)</FieldLabel>
                <TextContainer
                  value={filter.budget.min}
                  variant='outlined'
                  margin='dense'
                  placeholder='From'
                  onChange={(e) =>
                    onFilterChange({
                      ...filter,
                      budget: {
                        ...filter.budget,
                        min: e.target.value || undefined,
                      },
                    })
                  }
                  type='number'
                />
              </Box>
            </Grid>
            <Grid item>
              <TextContainer
                value={filter.budget.max}
                variant='outlined'
                margin='dense'
                placeholder='To'
                onChange={(e) =>
                  onFilterChange({
                    ...filter,
                    budget: {
                      ...filter.budget,
                      max: e.target.value || undefined,
                    },
                  })
                }
                type='number'
              />
            </Grid>
          </Grid>
        </Grid>
      </Grid>
    </Container>
  );
}
