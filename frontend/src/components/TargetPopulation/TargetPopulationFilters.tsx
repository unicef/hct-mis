import React from 'react';
import styled from 'styled-components';
import {
  TextField,
  InputAdornment,
  MenuItem,
  FormControl,
  Grid,
  Box,
} from '@material-ui/core';
import { Person, Search, Group } from '@material-ui/icons';
import Select from '../../shared/Select';
import InputLabel from '../../shared/InputLabel';
import { TARGETING_STATES } from '../../utils/constants';
import { ContainerWithBorder } from '../ContainerWithBorder';

const TextContainer = styled(TextField)`
  .MuiFilledInput-root {
    border-radius: 4px;
  }
  && {
    width: 232px;
    color: #5f6368;
    border-bottom: 0;
  }
  .MuiFilledInput-underline:before {
    border-bottom: 0;
  }
  .MuiFilledInput-underline:before {
    border-bottom: 0;
  }
  .MuiFilledInput-underline:hover {
    border-bottom: 0;
    border-radius: 4px;
  }
  .MuiFilledInput-underline:hover::before {
    border-bottom: 0;
  }
  .MuiFilledInput-underline::before {
    border-bottom: 0;
  }
  .MuiFilledInput-underline::after {
    border-bottom: 0;
  }
  .MuiFilledInput-underline::after:hover {
    border-bottom: 0;
  }
  .MuiSvgIcon-root {
    color: #5f6368;
  }
  .MuiFilledInput-input {
    padding: 10px 15px 10px;
  }
  .MuiInputAdornment-filled.MuiInputAdornment-positionStart:not(.MuiInputAdornment-hiddenLabel) {
    margin: 0px;
  }
`;

const StyledFormControl = styled(FormControl)`
  width: 232px;
  color: #5f6368;
  border-bottom: 0;
`;

const StartInputAdornment = styled(InputAdornment)`
  margin-right: 0;
`;
const FieldLabel = styled.span`
  font-size: 12px;
  color: rgba(0, 0, 0, 0.6);
`;

interface HouseholdFiltersProps {
  //targetPopulations: TargetPopulationNode[],
  onFilterChange;
  filter;
}
export function TargetPopulationFilters({
  // targetPopulations,
  onFilterChange,
  filter,
}: HouseholdFiltersProps): React.ReactElement {
  const handleFilterChange = (e, name): void =>
    onFilterChange({ ...filter, [name]: e.target.value });
  return (
    <ContainerWithBorder>
      <Grid container alignItems='flex-end' spacing={3}>
        <Grid item>
          <TextContainer
            placeholder='Search'
            variant='outlined'
            margin='dense'
            onChange={(e) => handleFilterChange(e, 'name')}
            InputProps={{
              startAdornment: (
                <InputAdornment position='start'>
                  <Search />
                </InputAdornment>
              ),
            }}
          />
        </Grid>
        <Grid item>
          <StyledFormControl variant='outlined' margin='dense'>
            <InputLabel>Status</InputLabel>
            <Select
              /* eslint-disable-next-line @typescript-eslint/ban-ts-ignore */
              // @ts-ignore
              onChange={(e) => handleFilterChange(e, 'status')}
              variant='outlined'
              label='Programme'
              InputProps={{
                startAdornment: (
                  <StartInputAdornment position='start'>
                    <Person />
                  </StartInputAdornment>
                ),
              }}
            >
              <MenuItem value=''>{TARGETING_STATES.NONE}</MenuItem>
              <MenuItem value='DRAFT'>{TARGETING_STATES.DRAFT}</MenuItem>
              <MenuItem value='APPROVED'>{TARGETING_STATES.APPROVED}</MenuItem>
              <MenuItem value='FINALIZED'>
                {TARGETING_STATES.FINALIZED}
              </MenuItem>
            </Select>
          </StyledFormControl>
        </Grid>
        <Grid item>
          <Box display='flex' flexDirection='column'>
            <FieldLabel>Number of Household</FieldLabel>
            <TextContainer
              id='minFilter'
              value={filter.numIndividuals.min}
              variant='outlined'
              margin='dense'
              placeholder='From'
              onChange={(e) =>
                onFilterChange({
                  ...filter,
                  numIndividuals: {
                    ...filter.numIndividuals,
                    min: e.target.value || undefined,
                  },
                })
              }
              type='number'
              InputProps={{
                startAdornment: (
                  <InputAdornment position='start'>
                    <Group />
                  </InputAdornment>
                ),
              }}
            />
          </Box>
        </Grid>
        <Grid item>
          <TextContainer
            id='maxFilter'
            value={filter.numIndividuals.max}
            variant='outlined'
            margin='dense'
            placeholder='To'
            onChange={(e) =>
              onFilterChange({
                ...filter,
                numIndividuals: {
                  ...filter.numIndividuals,
                  max: e.target.value || undefined,
                },
              })
            }
            type='number'
            InputProps={{
              startAdornment: (
                <InputAdornment position='start'>
                  <Group />
                </InputAdornment>
              ),
            }}
          />
        </Grid>
      </Grid>
    </ContainerWithBorder>
  );
}
