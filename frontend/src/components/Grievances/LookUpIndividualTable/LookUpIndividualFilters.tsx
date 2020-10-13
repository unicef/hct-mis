import React from 'react';
import styled from 'styled-components';
import SearchIcon from '@material-ui/icons/Search';
import CakeIcon from '@material-ui/icons/Cake';
import WcIcon from '@material-ui/icons/Wc';
import { InputAdornment, MenuItem, TextField } from '@material-ui/core';
import FormControl from '@material-ui/core/FormControl';
import { ContainerWithBorder } from '../../ContainerWithBorder';
import InputLabel from '../../../shared/InputLabel';
import Select from '../../../shared/Select';

const TextContainer = styled(TextField)`
  input[type='number']::-webkit-inner-spin-button,
  input[type='number']::-webkit-outer-spin-button {
    -webkit-appearance: none;
  }
  input[type='number'] {
    -moz-appearance: textfield;
  }
`;

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
}
export function LookUpIndividualFilters({
  onFilterChange,
  filter,
}: LookUpIndividualFiltersProps): React.ReactElement {
  const handleFilterChange = (e, name): void =>
    onFilterChange({ ...filter, [name]: e.target.value });
  return (
    <ContainerWithBorder>
      <SearchTextField
        label='Search'
        variant='outlined'
        margin='dense'
        value={filter.text}
        onChange={(e) => handleFilterChange(e, 'text')}
        InputProps={{
          startAdornment: (
            <InputAdornment position='start'>
              <SearchIcon />
            </InputAdornment>
          ),
        }}
        data-cy='filters-search'
      />
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
      <TextContainer
        variant='outlined'
        margin='dense'
        label='Age'
        value={filter.age.min}
        onChange={(e) =>
          onFilterChange({
            ...filter,
            age: { ...filter.age, min: e.target.value || undefined },
          })
        }
        type='number'
        InputProps={{
          startAdornment: (
            <InputAdornment position='start'>
              <CakeIcon />
            </InputAdornment>
          ),
        }}
      />
      to
      <TextContainer
        variant='outlined'
        margin='dense'
        label='Age'
        value={filter.age.max}
        onChange={(e) =>
          onFilterChange({
            ...filter,
            age: { ...filter.age, max: e.target.value || undefined },
          })
        }
        type='number'
        InputProps={{
          startAdornment: (
            <InputAdornment position='start'>
              <CakeIcon />
            </InputAdornment>
          ),
        }}
      />
    </ContainerWithBorder>
  );
}
