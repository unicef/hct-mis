import {
  FormControl,
  Grid,
  InputAdornment,
  MenuItem,
  TextField,
} from '@material-ui/core';
import { Search } from '@material-ui/icons';
import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import InputLabel from '../../../../shared/InputLabel';
import Select from '../../../../shared/Select';
import { useAllFieldsAttributesQuery } from '../../../../__generated__/graphql';
import { FlexFieldsTable } from '../../../tables/targeting/TargetPopulation/FlexFields';

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

const FilterWrapper = styled.div`
  padding: 20px;
`;

export function FlexFieldTab(): React.ReactElement {
  const { t } = useTranslation();
  const { data } = useAllFieldsAttributesQuery();
  const [searchValue, setSearchValue] = useState('');
  const [selectOptions, setSelectOptions] = useState([]);
  const [selectedOption, setSelectedOption] = useState('');
  const [selectedFieldType, setSelectedFieldType] = useState('All');
  useEffect(() => {
    if (data && !selectOptions.length) {
      const options = data.allFieldsAttributes.map((el) => el.associatedWith);
      const filteredOptions = options.filter(
        (item, index) => options.indexOf(item) === index,
      );
      setSelectOptions(filteredOptions);
    }
  }, [data, selectOptions]);
  if (!data) {
    return null;
  }

  return (
    <FilterWrapper>
      <Grid container spacing={3}>
        <Grid item>
          <TextContainer
            placeholder={t('Search')}
            variant='outlined'
            margin='dense'
            onChange={(e) => setSearchValue(e.target.value)}
            value={searchValue}
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
          {selectOptions.length && (
            <StyledFormControl variant='outlined' margin='dense'>
              <InputLabel>{t('Type')}</InputLabel>
              <Select
                /* eslint-disable-next-line @typescript-eslint/ban-ts-ignore */
                // @ts-ignore
                onChange={(e) => setSelectedOption(e.target.value)}
                variant='outlined'
                label='Type'
                value={selectedOption}
              >
                <MenuItem value=''>
                  <em>{t('All')}</em>
                </MenuItem>
                {selectOptions.map((type) => {
                  return (
                    <MenuItem key={type} value={type}>
                      {type}
                    </MenuItem>
                  );
                })}
              </Select>
            </StyledFormControl>
          )}
        </Grid>
        <Grid item>
          <StyledFormControl variant='outlined' margin='dense'>
            <InputLabel>{t('Field Type')}</InputLabel>
            <Select
              /* eslint-disable-next-line @typescript-eslint/ban-ts-ignore */
              // @ts-ignore
              onChange={(e) => setSelectedFieldType(e.target.value)}
              variant='outlined'
              label={t('Field Type')}
              value={selectedFieldType}
            >
              <MenuItem value={t('All')}>
                <em>{t('All')}</em>
              </MenuItem>
              {[
                { name: 'Flex field', value: 'Flex field' },
                { name: 'Core field', value: 'Core field' },
              ].map((el) => {
                return (
                  <MenuItem key={el.name} value={el.value}>
                    {el.name}
                  </MenuItem>
                );
              })}
            </Select>
          </StyledFormControl>
        </Grid>
      </Grid>
      <FlexFieldsTable
        selectedOption={selectedOption}
        searchValue={searchValue}
        selectedFieldType={selectedFieldType}
        fields={data.allFieldsAttributes}
      />
    </FilterWrapper>
  );
}
