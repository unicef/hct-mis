import CircularProgress from '@material-ui/core/CircularProgress';
import Autocomplete from '@material-ui/lab/Autocomplete';
import get from 'lodash/get';
import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useHistory, useLocation } from 'react-router-dom';
import styled from 'styled-components';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { useDebounce } from '../../hooks/useDebounce';
import { createHandleApplyFilterChange } from '../../utils/utils';
import { useAllUsersForFiltersLazyQuery } from '../../__generated__/graphql';
import TextField from '../TextField';

const StyledAutocomplete = styled(Autocomplete)`
  .MuiFormControl-marginDense {
    margin-top: 4px;
  }
  width: ${(props) => (props.fullWidth ? '100%' : '232px')};
`;

export const CreatedByAutocomplete = ({
  disabled,
  fullWidth = true,
  name,
  filter,
  value,
  label,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
  setFilter,
}: {
  disabled?: boolean;
  fullWidth?: boolean;
  name: string;
  filter;
  value: string;
  label?: string;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
  setFilter: (filter) => void;
}): React.ReactElement => {
  const { t } = useTranslation();
  const history = useHistory();
  const location = useLocation();
  const [open, setOpen] = useState(false);
  const [inputValue, onInputTextChange] = useState('');
  const debouncedInputText = useDebounce(inputValue, 500);
  const businessArea = useBusinessArea();

  const [loadData, { data, loading }] = useAllUsersForFiltersLazyQuery({
    variables: {
      businessArea,
      first: 100,
      orderBy: 'first_name,last_name,email',
      search: debouncedInputText,
      isTicketCreator: true,
    },
  });

  useEffect(() => {
    if (open) {
      loadData();
    }
  }, [open, debouncedInputText, loadData]);

  // load all users on mount to match the value from the url
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

  return (
    <StyledAutocomplete
      value={value}
      data-cy='filters-created-by-autocomplete'
      fullWidth={fullWidth}
      open={open}
      filterOptions={(options1) => options1}
      onChange={(_, selectedValue) =>
        handleFilterChange(name, selectedValue?.node?.id)
      }
      onOpen={() => {
        setOpen(true);
      }}
      onClose={(e, reason) => {
        setOpen(false);
        if (reason === 'select-option') return;
        onInputTextChange('');
      }}
      getOptionSelected={(option, value1) => {
        return option.node?.id === value1;
      }}
      getOptionLabel={(option) => {
        let optionLabel;
        if (option.node) {
          optionLabel = `${option.node.email}`;
        } else {
          optionLabel =
            data?.allUsers?.edges?.find((el) => el.node.id === option)?.node
              .email || '';
        }
        return `${optionLabel}`;
      }}
      disabled={disabled}
      options={get(data, 'allUsers.edges', [])}
      loading={loading}
      renderInput={(params) => (
        <TextField
          {...params}
          data-cy='filters-created-by-input'
          label={label || t('Created By')}
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
