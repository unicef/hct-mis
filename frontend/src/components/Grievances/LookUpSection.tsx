import { Box, Grid } from '@material-ui/core';
import React from 'react';
import { GRIEVANCE_CATEGORIES } from '../../utils/constants';
import { thingForSpecificGrievanceType } from '../../utils/utils';
import { LookUpHouseholdIndividual } from './LookUpHouseholdIndividual/LookUpHouseholdIndividual';
import { LookUpPaymentRecord } from './LookUpPaymentRecord/LookUpPaymentRecord';
import { LookUpRelatedTickets } from './LookUpRelatedTickets/LookUpRelatedTickets';

export const LookUpSection = ({
  onValueChange,
  values,
  disabledHouseholdIndividual,
  disabledPaymentRecords,
}: {
  onValueChange;
  values;
  disabledHouseholdIndividual?;
  disabledPaymentRecords?;
}): React.ReactElement => {
  const renderedLookupHouseholdIndividual = (
    <Grid item xs={6}>
      <Box p={3}>
        <LookUpHouseholdIndividual
          values={values}
          onValueChange={onValueChange}
          disabled={disabledHouseholdIndividual}
        />
      </Box>
    </Grid>
  );
  const renderedLookupRelatedTickets = (
    <Grid container>
      <Grid item xs={6}>
        <Box p={3}>
          <LookUpRelatedTickets values={values} onValueChange={onValueChange} />
        </Box>
      </Grid>
    </Grid>
  );
  const renderedLookupPaymentRecords = (
    <Grid item xs={6}>
      <Box p={3}>
        <LookUpPaymentRecord
          disabled={disabledPaymentRecords}
          values={values}
          onValueChange={onValueChange}
        />
      </Box>
    </Grid>
  );
  const allThree = (
    <Grid container alignItems='center'>
      {renderedLookupHouseholdIndividual}
      {renderedLookupPaymentRecords}
      {renderedLookupRelatedTickets}
    </Grid>
  );
  const lookupDict = {
    [GRIEVANCE_CATEGORIES.DATA_CHANGE]: (
      <Grid container alignItems='center'>
        <Grid container>{renderedLookupHouseholdIndividual}</Grid>
        {renderedLookupRelatedTickets}
      </Grid>
    ),
    [GRIEVANCE_CATEGORIES.SENSITIVE_GRIEVANCE]: allThree,
    [GRIEVANCE_CATEGORIES.GRIEVANCE_COMPLAINT]: allThree,
  };
  return thingForSpecificGrievanceType(
    { category: values.category },
    lookupDict,
    renderedLookupRelatedTickets,
    {
      [GRIEVANCE_CATEGORIES.NEGATIVE_FEEDBACK]: false,
      [GRIEVANCE_CATEGORIES.POSITIVE_FEEDBACK]: false,
      [GRIEVANCE_CATEGORIES.REFERRAL]: false,
      [GRIEVANCE_CATEGORIES.GRIEVANCE_COMPLAINT]: false,
      [GRIEVANCE_CATEGORIES.SENSITIVE_GRIEVANCE]: false,
      [GRIEVANCE_CATEGORIES.DATA_CHANGE]: false,
    },
  );
};
