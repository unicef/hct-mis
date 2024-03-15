import * as React from 'react';
import get from 'lodash/get';
import { Box, TextField } from '@mui/material';
import Autocomplete from '@mui/lab/Autocomplete';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { useDebounce } from '@hooks/useDebounce';
import { AllAdminAreasQuery, useAllAdminAreasQuery } from '@generated/graphql';
import { FieldLabel } from '@components/core/FieldLabel';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { useBaseUrl } from '@hooks/useBaseUrl';

const StyledAutocomplete = styled(Autocomplete)`
  width: 232px;
  .MuiFormControl-marginDense {
    margin-top: 4px;
  }
`;

export function AdminAreaAutocompleteMultiple({
  value,
  onChange,
  disabled,
  parentId,
}: {
  value;
  onChange;
  disabled?;
  parentId?;
}): React.ReactElement {
  const { t } = useTranslation();
  const [open, setOpen] = React.useState(false);
  const [inputValue, setInputTextChange] = React.useState('');

  const debouncedInputText = useDebounce(inputValue, 800);
  const [newValue, setNewValue] = useState([]);
  const { businessArea } = useBaseUrl();
  const { data, loading } = useAllAdminAreasQuery({
    variables: {
      first: 100,
      name: debouncedInputText,
      businessArea,
      parentId: parentId || '',
    },
  });
  useEffect(() => {
    setNewValue(value);
  }, [data, value]);
  useEffect(() => {
    setInputTextChange('');
  }, [value]);

  if (loading) return <LoadingComponent />;
  if (!data) return null;
  return (
    <Box display="flex" flexDirection="column">
      <FieldLabel>{t('Administrative Level 2')}</FieldLabel>
      {/*@ts-ignore */}
      <StyledAutocomplete<AllAdminAreasQuery['allAdminAreas']['edges'][number]>
        open={open}
        multiple
        fullWidth
        filterOptions={(options1) => options1}
        onChange={onChange}
        value={newValue}
        onOpen={() => {
          setOpen(true);
        }}
        onClose={() => {
          setOpen(false);
        }}
        isOptionEqualToValue={(option, value1) =>
          value1?.node?.id === option.node.id
        }
        getOptionLabel={(option) => {
          if (!option.node) {
            return '';
          }
          return `${option.node.name}`;
        }}
        disabled={disabled}
        options={get(data, 'allAdminAreas.edges', [])}
        loading={loading}
        renderInput={(params) => (
          <TextField
            {...params}
            inputProps={{
              ...params.inputProps,
              value: inputValue,
            }}
            size="small"
            placeholder={
              newValue.length > 0 ? null : t('Administrative Level 2')
            }
            variant="outlined"
            value={inputValue}
            onChange={(e) => setInputTextChange(e.target.value)}
          />
        )}
      />
    </Box>
  );
}
