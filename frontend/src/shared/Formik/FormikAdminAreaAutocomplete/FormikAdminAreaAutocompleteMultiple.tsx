import * as React from 'react';
import { AdminAreaAutocompleteMultiple } from '../../autocompletes/AdminAreaAutocompleteMultiple';

export function FormikAdminAreaAutocompleteMultiple({
  field,
  form,
  disabled,
  ...props
}): React.ReactElement {
  const handleChange = (e, option): void => {
    if (!option) {
      form.setFieldValue(field.name, null);
    } else {
      form.setFieldValue(field.name, option);
    }
  };
  return (
    <AdminAreaAutocompleteMultiple
      disabled={disabled}
      value={field.value}
      onChange={handleChange}
      {...props}
    />
  );
}
