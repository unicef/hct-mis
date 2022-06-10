import React from 'react';
import { InputAdornment } from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import moment from 'moment';
import get from 'lodash/get';
import TextField from '../../TextField';

export const FormikDateField = ({
  field,
  form,
  decoratorStart,
  decoratorEnd,
  label = null,
  placeholder = null,
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
      label={label}
      value={formattedValue || null}
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
          target: {
            value: moment(date).format('YYYY-MM-DD') || null,
            name: field.name,
          },
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
      renderInput={(params) => (
        <TextField placeholder={placeholder} {...params} />
      )}
    />
  );
};
