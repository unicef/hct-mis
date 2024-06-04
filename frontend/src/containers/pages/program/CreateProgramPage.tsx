import { Box, Step, StepButton, Stepper } from '@mui/material';
import { Formik } from 'formik';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  AllProgramsForChoicesDocument,
  ProgramPartnerAccess,
  useAllAreasTreeQuery,
  useCreateProgramMutation,
  useUserPartnerChoicesQuery,
} from '@generated/graphql';
import { ALL_PROGRAMS_QUERY } from '../../../apollo/queries/program/AllPrograms';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { DetailsStep } from '@components/programs/CreateProgram/DetailsStep';
import { PartnersStep } from '@components/programs/CreateProgram/PartnersStep';
import { programValidationSchema } from '@components/programs/CreateProgram/programValidationSchema';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import { hasPermissionInModule } from '../../../config/permissions';
import { usePermissions } from '@hooks/usePermissions';
import { BreadCrumbsItem } from '@components/core/BreadCrumbs';
import { useNavigate } from 'react-router-dom';

export const CreateProgramPage = (): ReactElement => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const permissions = usePermissions();
  const [step, setStep] = useState(0);
  const { showMessage } = useSnackbar();
  const { baseUrl, businessArea } = useBaseUrl();

  const { data: treeData, loading: treeLoading } = useAllAreasTreeQuery({
    variables: { businessArea },
  });
  const { data: userPartnerChoicesData, loading: userPartnerChoicesLoading } =
    useUserPartnerChoicesQuery();

  const [mutate] = useCreateProgramMutation({
    refetchQueries: () => [
      { query: ALL_PROGRAMS_QUERY, variables: { businessArea } },
    ],
  });

  const handleSubmit = async (values): Promise<void> => {
    const budgetValue = parseFloat(values.budget) ?? 0;
    const budgetToFixed = !Number.isNaN(budgetValue)
      ? budgetValue.toFixed(2)
      : 0;
    const populationGoalValue = parseInt(values.populationGoal, 10) ?? 0;
    const populationGoalParsed = !Number.isNaN(populationGoalValue)
      ? populationGoalValue
      : 0;
    const partnersToSet =
      values.partnerAccess === ProgramPartnerAccess.SelectedPartnersAccess
        ? values.partners.map(({ id, areas, areaAccess }) => ({
            partner: id,
            areas: areaAccess === 'ADMIN_AREA' ? areas : [],
            areaAccess,
          }))
        : [];
    const { editMode, ...requestValues } = values;

    try {
      const response = await mutate({
        variables: {
          programData: {
            ...requestValues,
            budget: budgetToFixed,
            populationGoal: populationGoalParsed,
            businessAreaSlug: businessArea,
            partners: partnersToSet,
          },
        },
        refetchQueries: () => [
          {
            query: AllProgramsForChoicesDocument,
            variables: { businessArea, first: 100 },
          },
        ],
      });
      showMessage('Programme created.');
      navigate(`/${baseUrl}/details/${response.data.createProgram.program.id}`);
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
    }
  };

  const initialValues = {
    editMode: false,
    name: '',
    programmeCode: '',
    startDate: '',
    endDate: '',
    sector: '',
    dataCollectingTypeCode: '',
    description: '',
    budget: '',
    administrativeAreasOfImplementation: '',
    populationGoal: '',
    cashPlus: false,
    frequencyOfPayments: 'REGULAR',
    partners: [],
    partnerAccess: ProgramPartnerAccess.AllPartnersAccess,
  };

  const stepFields = [
    [
      'name',
      'programmeCode',
      'startDate',
      'endDate',
      'sector',
      'dataCollectingTypeCode',
      'description',
      'budget',
      'administrativeAreasOfImplementation',
      'populationGoal',
      'cashPlus',
      'frequencyOfPayments',
    ],
    ['partnerAccess'],
  ];

  if (treeLoading || userPartnerChoicesLoading) return <LoadingComponent />;
  if (!treeData || !userPartnerChoicesData) return null;

  const { allAreasTree } = treeData;
  const { userPartnerChoices } = userPartnerChoicesData;

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Programme Management'),
      to: `/${baseUrl}/list/`,
    },
  ];

  return (
    <Formik
      initialValues={initialValues}
      onSubmit={(values) => {
        handleSubmit(values);
      }}
      initialTouched={{
        programmeCode: true,
      }}
      validationSchema={programValidationSchema(t)}
    >
      {({
        submitForm,
        values,
        validateForm,
        setFieldTouched,
        setFieldValue,
      }) => {
        const mappedPartnerChoices = userPartnerChoices
          .filter((partner) => partner.name !== 'UNICEF')
          .map((partner) => ({
            value: partner.value,
            label: partner.name,
            disabled: values.partners.some((p) => p.id === partner.value),
          }));

        const handleNext = async (): Promise<void> => {
          const errors = await validateForm();
          const step0Errors = stepFields[0].some((field) => errors[field]);

          if (step === 0 && !step0Errors) {
            setStep(1);
          } else {
            stepFields[step].forEach((field) => setFieldTouched(field));
          }
        };

        return (
          <>
            <PageHeader
              title={t('New Programme')}
              breadCrumbs={
                hasPermissionInModule(
                  'PROGRAMME_VIEW_LIST_AND_DETAILS',
                  permissions,
                )
                  ? breadCrumbsItems
                  : null
              }
            />
            <Box p={6}>
              <Box mb={2}>
                <Stepper activeStep={step}>
                  <Step>
                    <StepButton
                      data-cy="step-button-details"
                      onClick={() => setStep(0)}
                    >
                      {t('Details')}
                    </StepButton>
                  </Step>
                  <Step>
                    <StepButton
                      data-cy="step-button-partners"
                      onClick={() => setStep(1)}
                    >
                      {t('Programme Partners')}
                    </StepButton>
                  </Step>
                </Stepper>
              </Box>
              {step === 0 && (
                <DetailsStep values={values} handleNext={handleNext} />
              )}
              {step === 1 && (
                <PartnersStep
                  values={values}
                  allAreasTreeData={allAreasTree}
                  partnerChoices={mappedPartnerChoices}
                  step={step}
                  setStep={setStep}
                  submitForm={submitForm}
                  setFieldValue={setFieldValue}
                />
              )}
            </Box>
          </>
        );
      }}
    </Formik>
  );
};
