import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import get from 'lodash/get';
import { InputAdornment } from '@material-ui/core';
import RoomRoundedIcon from '@material-ui/icons/RoomRounded';
import CircularProgress from '@material-ui/core/CircularProgress';
import Autocomplete from '@material-ui/lab/Autocomplete';
import { useDebounce } from '../../hooks/useDebounce';
import TextField from '../../shared/TextField';
import {
  AllAdminAreasQuery,
  useAllAdminAreasQuery,
} from '../../__generated__/graphql';
import { useBusinessArea } from '../../hooks/useBusinessArea';

const StyledAutocomplete = styled(Autocomplete)`
  width: 232px;
  .MuiFormControl-marginDense {
    margin-top: 4px;
  }
`;

export function AdminAreaFixedAutocomplete({
  value,
  onChange,
  disabled,
}: {
  value;
  onChange;
  disabled?;
}): React.ReactElement {
  const [open, setOpen] = React.useState(false);
  const [inputValue, onInputTextChange] = React.useState('');

  const debouncedInputText = useDebounce(inputValue, 500);
  const [newValue, setNewValue] = useState(null);
  const businessArea = useBusinessArea();
  const { data, loading } = useAllAdminAreasQuery({
    variables: {
      title: debouncedInputText,
      businessArea,
    },
  });

  useEffect(() => {
    if (data) {
      setNewValue(
        typeof value === 'string'
          ? data.allAdminAreas.edges.find((item) => item.node.title === value)
          : value,
      );
    } else {
      setNewValue(null);
    }
    onInputTextChange('');
  }, [data, value]);

  return (
    <StyledAutocomplete<AllAdminAreasQuery['allAdminAreas']['edges'][number]>
      open={open}
      filterOptions={(options1) => options1}
      onChange={onChange}
      value={newValue}
      onOpen={() => {
        setOpen(true);
      }}
      onClose={() => {
        setOpen(false);
      }}
      getOptionSelected={(option, selectedValue) => {
        return selectedValue && selectedValue.node.id === option.node.id;
      }}
      getOptionLabel={(option) => {
        if (!option.node) {
          return '';
        }
        return `${option.node.title}`;
      }}
      disabled={disabled}
      options={get(data, 'allAdminAreas.edges', [])}
      loading={loading}
      renderInput={(params) => (
        <TextField
          {...params}
          label='Administrative Level 2'
          variant='outlined'
          margin='dense'
          value={inputValue}
          onChange={(e) => onInputTextChange(e.target.value)}
          InputProps={{
            ...params.InputProps,
            startAdornment: (
              <InputAdornment position='start'>
                <RoomRoundedIcon style={{ color: '#5f6368' }} />
              </InputAdornment>
            ),
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
}
