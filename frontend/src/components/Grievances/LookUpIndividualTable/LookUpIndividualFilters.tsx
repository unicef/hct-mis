import React from 'react';
import styled from 'styled-components';
import moment from 'moment';
import SearchIcon from '@material-ui/icons/Search';
import WcIcon from '@material-ui/icons/Wc';
import FlashOnIcon from '@material-ui/icons/FlashOn';
import {
  Box,
  Button,
  Grid,
  InputAdornment,
  MenuItem,
  TextField,
} from '@material-ui/core';
import { KeyboardDatePicker } from '@material-ui/pickers';
import FormControl from '@material-ui/core/FormControl';
import { ContainerWithBorder } from '../../ContainerWithBorder';
import InputLabel from '../../../shared/InputLabel';
import Select from '../../../shared/Select';
import { FieldLabel } from '../../FieldLabel';
import { AdminAreasAutocomplete } from '../../population/AdminAreaAutocomplete';

const StyledFormControl = styled(FormControl)`
  width: 232px;
  color: #5f6368;
  border-bottom: 0;
`;

const SearchTextField = styled(TextField)`
  flex: 1;
  && {
    min-width: 150px;
  }
`;
const StartInputAdornment = styled(InputAdornment)`
  margin-right: 0;
`;

interface LookUpIndividualFiltersProps {
  onFilterChange;
  filter;
  programs;
  setFilterIndividualApplied?;
  individualFilterInitial?;
}
export function LookUpIndividualFilters({
  onFilterChange,
  filter,
  programs,
  setFilterIndividualApplied,
  individualFilterInitial,
}: LookUpIndividualFiltersProps): React.ReactElement {
  const handleFilterChange = (e, name): void =>
    onFilterChange({ ...filter, [name]: e.target.value });
  return (
    <ContainerWithBorder>
      <Grid container alignItems='flex-end' spacing={3}>
        <Grid item>
          <SearchTextField
            label='Search'
            variant='outlined'
            margin='dense'
            value={filter.search}
            onChange={(e) => handleFilterChange(e, 'search')}
            InputProps={{
              startAdornment: (
                <InputAdornment position='start'>
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
            data-cy='filters-search'
          />
        </Grid>
        <Grid item>
          <StyledFormControl variant='outlined' margin='dense'>
            <InputLabel>Programme</InputLabel>
            <Select
              /* eslint-disable-next-line @typescript-eslint/ban-ts-ignore */
              // @ts-ignore
              onChange={(e) => handleFilterChange(e, 'programs')}
              variant='outlined'
              label='Programme'
              value={filter.programs || []}
              InputProps={{
                startAdornment: (
                  <StartInputAdornment position='start'>
                    <FlashOnIcon />
                  </StartInputAdornment>
                ),
              }}
            >
              <MenuItem value=''>
                <em>None</em>
              </MenuItem>
              {programs.map((program) => (
                <MenuItem key={program.id} value={program.id}>
                  {program.name}
                </MenuItem>
              ))}
            </Select>
          </StyledFormControl>
        </Grid>
        <Grid item>
          <Box display='flex' flexDirection='column'>
            <FieldLabel>Registration Date</FieldLabel>
            <KeyboardDatePicker
              variant='inline'
              inputVariant='outlined'
              margin='dense'
              placeholder='From'
              autoOk
              onChange={(date) =>
                onFilterChange({
                  ...filter,
                  lastRegistrationDate: {
                    ...filter.lastRegistrationDate,
                    min: date ? moment(date).format('YYYY-MM-DD') : null,
                  },
                })
              }
              value={filter.lastRegistrationDate.min || null}
              format='YYYY-MM-DD'
              InputAdornmentProps={{ position: 'end' }}
            />
          </Box>
        </Grid>
        <Grid item>
          <KeyboardDatePicker
            variant='inline'
            inputVariant='outlined'
            margin='dense'
            placeholder='To'
            autoOk
            onChange={(date) =>
              onFilterChange({
                ...filter,
                lastRegistrationDate: {
                  ...filter.lastRegistrationDate,
                  max: date ? moment(date).format('YYYY-MM-DD') : null,
                },
              })
            }
            value={filter.lastRegistrationDate.max || null}
            format='YYYY-MM-DD'
            InputAdornmentProps={{ position: 'end' }}
          />
        </Grid>
        <Grid item>
          <StyledFormControl variant='outlined' margin='dense'>
            <InputLabel>Status</InputLabel>
            <Select
              /* eslint-disable-next-line @typescript-eslint/ban-ts-ignore */
              // @ts-ignore
              onChange={(e) => handleFilterChange(e, 'status')}
              multiple
              variant='outlined'
              label='Status'
              value={filter.status || []}
            >
              {[
                { value: 'ACTIVE', name: 'Active' },
                { value: 'WITHDRAWN', name: 'Withdrawn' },
                { value: 'DUPLICATE', name: 'Duplicate' },
              ].map((item) => {
                return (
                  <MenuItem key={item.value} value={item.value}>
                    {item.name}
                  </MenuItem>
                );
              })}
            </Select>
          </StyledFormControl>
        </Grid>
        <Grid item>
          <AdminAreasAutocomplete
            onFilterChange={onFilterChange}
            name='admin2'
            value={filter.admin2}
          />
        </Grid>
        <Grid item>
          <StyledFormControl variant='outlined' margin='dense'>
            <InputLabel>Gender</InputLabel>
            <Select
              /* eslint-disable-next-line @typescript-eslint/ban-ts-ignore */
              // @ts-ignore
              onChange={(e) => handleFilterChange(e, 'sex')}
              variant='outlined'
              value={filter.sex || ''}
              label='Gender'
              InputProps={{
                startAdornment: (
                  <StartInputAdornment position='start'>
                    <WcIcon />
                  </StartInputAdornment>
                ),
              }}
              SelectDisplayProps={{
                'data-cy': 'filters-sex',
              }}
              MenuProps={{
                'data-cy': 'filters-sex-options',
              }}
            >
              <MenuItem value=''>
                <em>None</em>
              </MenuItem>
              <MenuItem value='MALE'>Male</MenuItem>
              <MenuItem value='FEMALE'>Female</MenuItem>
            </Select>
          </StyledFormControl>
        </Grid>
        <Grid container justify='flex-end'>
          <Button
            color='primary'
            onClick={() => {
              setFilterIndividualApplied(individualFilterInitial);
              onFilterChange(individualFilterInitial);
            }}
          >
            Clear
          </Button>
          <Button
            color='primary'
            variant='outlined'
            onClick={() => setFilterIndividualApplied(filter)}
          >
            Apply
          </Button>
        </Grid>
      </Grid>
    </ContainerWithBorder>
  );
}
