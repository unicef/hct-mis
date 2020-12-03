import { Box, FormHelperText, Typography } from '@material-ui/core';
import React, { useState } from 'react';
import { isInvalid } from '../../../utils/utils';
import { LookUpButton } from '../LookUpButton';
import { LookUpHouseholdIndividualDisplay } from './LookUpHouseholdIndividualDisplay';
import { LookUpHouseholdIndividualModal } from './LookUpHouseholdIndividualModal';

export const LookUpHouseholdIndividual = ({
  onValueChange,
  values,
  disabled,
  errors,
  touched,
}: {
  onValueChange;
  values;
  disabled?: boolean;
  errors?;
  touched?;
}): React.ReactElement => {
  const [lookUpDialogOpen, setLookUpDialogOpen] = useState(false);

  return (
    <>
      <Box display='flex' flexDirection='column'>
        {values.selectedHousehold || values.selectedIndividual || disabled ? (
          <LookUpHouseholdIndividualDisplay
            setLookUpDialogOpen={setLookUpDialogOpen}
            values={values}
            disabled={disabled}
            onValueChange={onValueChange}
          />
        ) : (
          <LookUpButton
            title='Look up Household / Individual'
            handleClick={() => setLookUpDialogOpen(true)}
          />
        )}
        {isInvalid('selectedIndividual', errors, touched) && (
          <FormHelperText error>{errors?.selectedIndividual}</FormHelperText>
        )}
        {isInvalid('selectedHousehold', errors, touched) && (
          <FormHelperText error>{errors?.selectedHousehold}</FormHelperText>
        )}
      </Box>

      <LookUpHouseholdIndividualModal
        lookUpDialogOpen={lookUpDialogOpen}
        setLookUpDialogOpen={setLookUpDialogOpen}
        initialValues={values}
        onValueChange={onValueChange}
      />
    </>
  );
};
