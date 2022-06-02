import { Box, Grid, InputAdornment, MenuItem } from '@material-ui/core';
import CakeIcon from '@material-ui/icons/Cake';
import SearchIcon from '@material-ui/icons/Search';
import WcIcon from '@material-ui/icons/Wc';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import InputLabel from '../../shared/InputLabel';
import Select from '../../shared/Select';
import TextField from '../../shared/TextField';
import { ContainerWithBorder } from '../core/ContainerWithBorder';
import { FieldLabel } from '../core/FieldLabel';
import { IndividualChoiceDataQuery } from '../../__generated__/graphql';
import { AdminAreaAutocomplete } from './AdminAreaAutocomplete';
import { StyledFormControl } from '../StyledFormControl';

const TextContainer = styled(TextField)`
  input[type='number']::-webkit-inner-spin-button,
  input[type='number']::-webkit-outer-spin-button {
    -webkit-appearance: none;
  }
  input[type='number'] {
    -moz-appearance: textfield;
  }
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

interface IndividualsFilterProps {
  onFilterChange;
  filter;
  choicesData: IndividualChoiceDataQuery;
}

export function IndividualsFilter({
  onFilterChange,
  filter,
  choicesData,
}: IndividualsFilterProps): React.ReactElement {
  const { t } = useTranslation();
  const handleFilterChange = (e, name): void =>
    onFilterChange({ ...filter, [name]: e.target.value });
  return (
    <ContainerWithBorder>
      <Grid container alignItems='flex-end' spacing={3}>
        <Grid item>
          <SearchTextField
            label={t('Search')}
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
        </Grid>
        <Grid item>
          <AdminAreaAutocomplete
            onFilterChange={onFilterChange}
            name='adminArea'
          />
        </Grid>
        <Grid item>
          <StyledFormControl variant='outlined' margin='dense'>
            <InputLabel>{t('Gender')}</InputLabel>
            <Select
              /* eslint-disable-next-line @typescript-eslint/ban-ts-ignore */
              // @ts-ignore
              onChange={(e) => handleFilterChange(e, 'sex')}
              variant='outlined'
              value={filter.sex || ''}
              label={t('Gender')}
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
                <em>{t('None')}</em>
              </MenuItem>
              <MenuItem value='MALE'>{t('Male')}</MenuItem>
              <MenuItem value='FEMALE'>{t('Female')}</MenuItem>
            </Select>
          </StyledFormControl>
        </Grid>
        <Grid item>
          <Box display='flex' flexDirection='column'>
            <FieldLabel>Age</FieldLabel>
            <TextContainer
              variant='outlined'
              margin='dense'
              placeholder={t('From')}
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
          </Box>
        </Grid>
        <Grid item>
          <TextContainer
            variant='outlined'
            margin='dense'
            placeholder={t('To')}
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
        </Grid>
        <Grid item>
          <StyledFormControl variant='outlined' margin='dense'>
            <InputLabel>{t('Flags')}</InputLabel>
            <Select
              /* eslint-disable-next-line @typescript-eslint/ban-ts-ignore */
              // @ts-ignore
              onChange={(e) => handleFilterChange(e, 'flags')}
              variant='outlined'
              label={t('Flags')}
              multiple
              value={filter.flags}
              SelectDisplayProps={{ 'data-cy': 'filters-flags' }}
              MenuProps={{
                'data-cy': 'filters-flags-options',
              }}
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
            </Select>
          </StyledFormControl>
        </Grid>
      </Grid>
    </ContainerWithBorder>
  );
}
