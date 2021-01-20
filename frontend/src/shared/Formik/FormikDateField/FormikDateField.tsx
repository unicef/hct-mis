import React from 'react';
import { InputAdornment } from '@material-ui/core';
import { DatePicker } from '@material-ui/pickers';
import moment from 'moment';
import get from 'lodash/get';

export const FormikDateField = ({
  field,
  form,
  decoratorStart,
  decoratorEnd,
  ...otherProps
}): React.ReactElement => {
  const isInvalid =
    get(form.errors, field.name) &&
    (get(form.touched, field.name) || form.submitCount > 0);
  const dateFormat = 'YYYY-MM-DD';
  let formattedValue = field.value === '' ? null : field.value;
  if (formattedValue) {
    formattedValue = moment(formattedValue).toISOString();
  }

  return (
    <DatePicker
      {...field}
      {...otherProps}
      name={field.name}
      variant='inline'
      inputVariant='outlined'
      margin='dense'
      value={formattedValue}
      error={isInvalid}
      onBlur={null}
      helperText={isInvalid && get(form.errors, field.name)}
      autoOk
      onClose={() => {
        setTimeout(() => {
          form.handleBlur({ target: { name: field.name } });
        }, 0);
      }}
      onChange={(date) => {
        field.onChange({
          target: { value: date.format('YYYY-MM-DD'), name: field.name },
        });
      }}
      format={dateFormat}
      InputProps={{
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
        'data-cy': `date-input-${field.name}`,
      }}
      PopoverProps={{
        PaperProps: { 'data-cy': 'date-picker-container' },
      }}
    />
  );
};
