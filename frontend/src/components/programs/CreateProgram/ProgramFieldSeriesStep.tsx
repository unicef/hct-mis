import { useConfirmation } from '@components/core/ConfirmationDialog';
import { DividerLine } from '@components/core/DividerLine';
import { PduSubtypeChoicesDataQuery } from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import { Box, Button, FormControl, Grid, IconButton } from '@mui/material';
import { FormikSelectField } from '@shared/Formik/FormikSelectField';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { Field, FieldArray } from 'formik';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';

interface ProgramFieldSeriesStepProps {
  values: {
    pduFields: Array<any>;
  };
  handleNext?: () => Promise<void>;
  setStep: (step: number) => void;
  step: number;
  programHasRdi?: boolean;
  pdusubtypeChoicesData?: PduSubtypeChoicesDataQuery;
  errors: any;
  programId?: string;
}

export const ProgramFieldSeriesStep = ({
  values,
  handleNext,
  setStep,
  step,
  programHasRdi,
  pdusubtypeChoicesData,
  errors,
  programId: formProgramId,
}: ProgramFieldSeriesStepProps) => {
  const { t } = useTranslation();
  const { businessArea, programId, baseUrl } = useBaseUrl();
  const confirm = useConfirmation();

  const mappedPduSubtypeChoices = pdusubtypeChoicesData?.pduSubtypeChoices.map(
    (el) => ({
      value: el.value,
      name: el.displayName,
    }),
  );

  const confirmationModalTitle = t('Deleting Time Series Field');
  const confirmationText = t(
    'Are you sure you want to delete this field? This action cannot be reversed.',
  );

  return (
    <>
      <FieldArray
        name="pduFields"
        render={(arrayHelpers) => (
          <div>
            {values.pduFields && values.pduFields.length > 0
              ? values.pduFields.map((_field, index) => (
                  <Box key={index} pt={3} pb={3}>
                    <Grid container spacing={3} alignItems="flex-start">
                      <Grid item xs={3}>
                        <Field
                          name={`pduFields.${index}.label`}
                          required
                          fullWidth
                          variant="outlined"
                          label={t('Time Series Field Name')}
                          component={FormikTextField}
                          disabled={programHasRdi}
                        />
                      </Grid>
                      <Grid item xs={3}>
                        <Field
                          name={`pduFields.${index}.pduData.subtype`}
                          required
                          fullWidth
                          variant="outlined"
                          label={t('Data Type')}
                          component={FormikSelectField}
                          choices={mappedPduSubtypeChoices}
                          disabled={programHasRdi}
                        />
                      </Grid>
                      <Grid item xs={3}>
                        <Field
                          name={`pduFields.${index}.pduData.numberOfRounds`}
                          fullWidth
                          required
                          variant="outlined"
                          label={t('Number of Expected Rounds')}
                          onChange={(e) => {
                            const numberOfRounds = parseInt(e.target.value, 10);
                            if (!isNaN(numberOfRounds) && numberOfRounds > 0) {
                              const currentRoundsNames =
                                values.pduFields[index].pduData.roundsNames ||
                                [];
                              let newRoundsNames;

                              if (numberOfRounds > currentRoundsNames.length) {
                                newRoundsNames = [
                                  ...currentRoundsNames,
                                  ...Array(
                                    numberOfRounds - currentRoundsNames.length,
                                  ).fill(''),
                                ];
                              } else {
                                newRoundsNames = currentRoundsNames.slice(
                                  0,
                                  numberOfRounds,
                                );
                              }

                              // Update the form state using setFieldValue
                              arrayHelpers.form.setFieldValue(
                                `pduFields.${index}.pduData.roundsNames`,
                                newRoundsNames,
                              );
                              arrayHelpers.form.setFieldValue(
                                `pduFields.${index}.pduData.numberOfRounds`,
                                numberOfRounds,
                              );
                            }
                          }}
                          component={FormikSelectField}
                          choices={[...Array(10).keys()].map((n) => ({
                            value: n + 1,
                            label: `${n + 1}`,
                          }))}
                          disabled={programHasRdi}
                        />
                      </Grid>
                      <Grid item xs={1}>
                        <IconButton
                          onClick={() =>
                            confirm({
                              title: confirmationModalTitle,
                              content: confirmationText,
                              type: 'error',
                            }).then(() => arrayHelpers.remove(index))
                          }
                          disabled={programHasRdi}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Grid>
                      {_field.pduData.numberOfRounds &&
                        [
                          ...Array(
                            Number(_field.pduData.numberOfRounds),
                          ).keys(),
                        ].map((round) => (
                          <Grid item xs={12} key={round}>
                            <FormControl fullWidth variant="outlined">
                              <Field
                                name={`pduFields.${index}.pduData.roundsNames.${round}`}
                                fullWidth
                                variant="outlined"
                                label={`${t('Round')} ${round + 1} ${t('Name')}`}
                                component={FormikTextField}
                                type="text"
                                disabled={programHasRdi}
                              />
                            </FormControl>
                          </Grid>
                        ))}
                    </Grid>
                    {values.pduFields.length > 1 &&
                      index < values.pduFields.length - 1 && <DividerLine />}
                  </Box>
                ))
              : null}
            <Box mt={6}>
              <Button
                variant="outlined"
                color="primary"
                onClick={() =>
                  arrayHelpers.push({
                    label: '',
                    pduData: {
                      subtype: '',
                      numberOfRounds: null,
                      roundsNames: [],
                    },
                  })
                }
                endIcon={<AddIcon />}
                disabled={programHasRdi}
                data-cy="button-add-time-series-field"
              >
                {t('Add Time Series Fields')}
              </Button>
            </Box>
          </div>
        )}
      />
      <Box mt={3} display="flex" justifyContent="space-between">
        <Button
          data-cy="button-cancel"
          component={Link}
          to={
            formProgramId
              ? `/${businessArea}/programs/${programId}/details/${formProgramId}`
              : `/${baseUrl}/list`
          }
        >
          {t('Cancel')}
        </Button>
        <Box display="flex">
          <Box mr={2}>
            <Button
              data-cy="button-back"
              variant="outlined"
              onClick={() => setStep(step - 1)}
            >
              {t('Back')}
            </Button>
          </Box>
          <Button
            variant="contained"
            color="primary"
            data-cy="button-next"
            onClick={handleNext}
            disabled={errors.pduFields && errors.pduFields.length > 0}
          >
            {t('Next')}
          </Button>
        </Box>
      </Box>
    </>
  );
};
