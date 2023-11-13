import CircularProgress from '@material-ui/core/CircularProgress';
import Autocomplete from '@material-ui/lab/Autocomplete';
import { useHistory, useLocation } from 'react-router-dom';
import get from 'lodash/get';
import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { useDebounce } from '../../hooks/useDebounce';
import { useRdiAutocompleteLazyQuery } from '../../__generated__/graphql';
import TextField from '../TextField';
import { createHandleApplyFilterChange } from '../../utils/utils';
import { useBaseUrl } from '../../hooks/useBaseUrl';

const StyledAutocomplete = styled(Autocomplete)`
  width: ${(props) => (props.fullWidth ? '100%' : '232px')}
    .MuiFormControl-marginDense {
    margin-top: 4px;
  }
`;

export const RdiAutocomplete = ({
  disabled,
  fullWidth = true,
  name,
  filter,
  value,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
  setFilter,
  dataCy,
}: {
  disabled?;
  fullWidth?: boolean;
  name: string;
  filter?;
  value?: string;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
  setFilter: (filter) => void;
  dataCy?: string;
}): React.ReactElement => {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const history = useHistory();
  const location = useLocation();
  const [inputValue, onInputTextChange] = useState('');
  const debouncedInputText = useDebounce(inputValue, 500);
  const { businessArea } = useBaseUrl();
  const [loadData, { data, loading }] = useRdiAutocompleteLazyQuery({
    variables: {
      businessArea,
      first: 20,
      orderBy: 'name',
      name: debouncedInputText,
    },
    fetchPolicy: 'cache-and-network',
  });
  useEffect(() => {
    if (open) {
      loadData();
    }
  }, [open, debouncedInputText, loadData]);

  // load all rdi on mount to match the value from the url
  useEffect(() => {
    loadData();
  }, [loadData]);

  const { handleFilterChange } = createHandleApplyFilterChange(
    initialFilter,
    history,
    location,
    filter,
    setFilter,
    appliedFilter,
    setAppliedFilter,
  );

  if (!data) return null;

  return (
    <StyledAutocomplete
      value={value}
      fullWidth={fullWidth}
      data-cy={dataCy}
      open={open}
      filterOptions={(options1) => options1}
      onChange={(_, selectedValue) => {
        if (selectedValue?.node?.id) {
          handleFilterChange(name, selectedValue.node.id);
        }
      }}
      onOpen={() => {
        setOpen(true);
      }}
      onClose={(e, reason) => {
        setOpen(false);
        if (reason === 'select-option') return;
        onInputTextChange('');
      }}
      getOptionSelected={(option, value1) => {
        return value1 === option.node.id;
      }}
      getOptionLabel={(option) => {
        let label;
        if (option.node) {
          label = `${option.node.name}`;
        } else {
          const foundRdi = data?.allRegistrationDataImports?.edges?.find(
            (el) => el.node.id === option,
          )?.node.name;
          label = foundRdi ? `${foundRdi}` : inputValue;
        }
        return `${label}`;
      }}
      disabled={disabled}
      options={get(data, 'allRegistrationDataImports.edges', [])}
      loading={loading}
      renderInput={(params) => (
        <TextField
          {...params}
          label={t('Registration Data Import')}
          variant='outlined'
          margin='dense'
          value={inputValue}
          onChange={(e) => onInputTextChange(e.target.value)}
          InputProps={{
            ...params.InputProps,
            endAdornment: (
              <>
                {loading ? (
                  <CircularProgress color='inherit' size={20} />
                ) : null}
                {params.InputProps.endAdornment}
              </>
            ),
          }}
        />
      )}
    />
  );
};
