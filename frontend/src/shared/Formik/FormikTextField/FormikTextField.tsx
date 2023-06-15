import React from 'react';
import { InputAdornment, TextField } from '@material-ui/core';
import styled from 'styled-components';
import get from 'lodash/get';

const StyledTextField = styled(TextField)`
  input[type='number']::-webkit-inner-spin-button,
  input[type='number']::-webkit-outer-spin-button {
    -webkit-appearance: none;
  }
  input[type='number'] {
    -moz-appearance: textfield;
  }
  .MuiFormHelperText-root {
    white-space: pre-line;
  }
`;

export const FormikTextField = ({
  field,
  form,
  decoratorStart,
  decoratorEnd,
  type,
  precision,
  integer,
  maxLength,
  ...otherProps
}): React.ReactElement => {
  const isInvalid =
    get(form.errors, field.name) &&
    (get(form.touched, field.name) || form.submitCount > 0);
  const handleKeyPress = (evt): void => {
    if (type === 'number' && ['e', 'E', '+', '-'].includes(evt.key)) {
      evt.preventDefault();
    }
    if (integer && [',', '.'].includes(evt.key)) {
      evt.preventDefault();
    }
  };

  const onBlur = (e): void => {
    const newEvent = { ...e };
    if (type === 'number' && precision !== undefined) {
      newEvent.target.value = parseFloat(e.target.value).toFixed(2);
    }
    form.handleBlur(newEvent);
  };

  return (
    <>
      <StyledTextField
        {...field}
        {...otherProps}
        name={field.name}
        id={`textField-${field.name}`}
        margin='dense'
        value={field.value}
        onChange={form.handleChange}
        onBlur={onBlur}
        error={isInvalid}
        autoComplete='off'
        type={type}
        helperText={isInvalid && get(form.errors, field.name)}
        InputProps={{
          onKeyPress: handleKeyPress,
          startAdornment: decoratorStart && (
            <InputAdornment position='start'>{decoratorStart}</InputAdornment>
          ),
          endAdornment: decoratorEnd && (
            <InputAdornment position='end'>{decoratorEnd}</InputAdornment>
          ),
        }}
        // https://github.com/mui-org/material-ui/issues/12805
        // eslint-disable-next-line react/jsx-no-duplicate-props
        inputProps={{
          'data-cy': `input-${field.name}`,
          maxLength: maxLength || null,
        }}
      />
    </>
  );
};
