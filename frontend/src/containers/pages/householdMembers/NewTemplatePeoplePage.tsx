import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { BreadCrumbsItem } from '@components/core/BreadCrumbs';
import { PageHeader } from '@components/core/PageHeader';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { useTranslation } from 'react-i18next';
import { hasPermissions, PERMISSIONS } from 'src/config/permissions';
import { BaseSection } from '@components/core/BaseSection';
import { Button, Stepper, Step, StepLabel, Box } from '@mui/material';
import { getFilterFromQueryParams } from '@utils/utils';
import { FilterIndividuals } from '@components/periodicDataUpdates/FilterIndividuals';
import { FieldsToUpdate } from '@components/periodicDataUpdates/FieldsToUpdate';
import { Formik } from 'formik';

export const NewTemplatePeoplePage = (): React.ReactElement => {
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();
  const permissions = usePermissions();
  const location = useLocation();

  const initialFilter = {
    registrationDataImport: '',
    genderIdentity: '',
    ageMin: null,
    ageMax: null,
    hasGrievanceTicket: '',
    receivedAssistance: '',
    householdSizeMin: null,
    householdSizeMax: null,
  };

  const [filter, setFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const [appliedFilter, setAppliedFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );

  const initialValues = {
    ...appliedFilter,
    selectedFields: [],
  };

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('People'),
      to: `/${baseUrl}/population/people`,
    },
  ];

  const [activeStep, setActiveStep] = useState(0);
  const steps = ['Filter Individuals', 'Fields to Update'];

  const handleNext = () => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  return (
    <Formik
      initialValues={initialValues}
      onSubmit={(values) => {
        console.log('values', values);
      }}
    >
      {({ values, setFieldValue, submitForm }) => (
        <>
          <PageHeader
            title={t('New Template Page')}
            breadCrumbs={
              hasPermissions(
                PERMISSIONS.POPULATION_VIEW_HOUSEHOLDS_LIST,
                permissions,
              )
                ? breadCrumbsItems
                : null
            }
          />
          <BaseSection>
            <Stepper activeStep={activeStep} alternativeLabel>
              {steps.map((label) => (
                <Step key={label}>
                  <StepLabel>{label}</StepLabel>
                </Step>
              ))}
            </Stepper>
            {activeStep === 0 && (
              <FilterIndividuals
                isOnPaper={false}
                filter={filter}
                setFilter={setFilter}
                initialFilter={initialFilter}
                appliedFilter={appliedFilter}
                setAppliedFilter={setAppliedFilter}
              />
            )}
            {activeStep === 1 && (
              <FieldsToUpdate values={values} setFieldValue={setFieldValue} />
            )}
            <Box display="flex" mt={4} justifyContent="flex-start" width="100%">
              <Box mr={1}>
                <Button
                  variant="outlined"
                  color="secondary"
                  component={Link}
                  to={`/${baseUrl}/population/people`}
                  style={{ marginRight: '10px' }}
                  data-cy="cancel-button"
                >
                  Cancel
                </Button>
              </Box>
              <Box display="flex">
                {activeStep === 1 && (
                  <Box mr={1}>
                    <Button
                      data-cy="back-button"
                      variant="outlined"
                      onClick={handleBack}
                    >
                      Back
                    </Button>
                  </Box>
                )}
                <Box>
                  <Button
                    variant="contained"
                    data-cy="submit-button"
                    color="primary"
                    onClick={activeStep === 1 ? submitForm : handleNext}
                  >
                    {activeStep === 1 ? 'Generate Template' : 'Next'}
                  </Button>
                </Box>
              </Box>
            </Box>
          </BaseSection>
        </>
      )}
    </Formik>
  );
};
