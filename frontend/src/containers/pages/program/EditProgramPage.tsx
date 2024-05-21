import { Box, Step, StepButton, Stepper } from '@mui/material';
import { Formik } from 'formik';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate, useParams } from 'react-router-dom';
import {
  ProgramPartnerAccess,
  useAllAreasTreeQuery,
  useProgramQuery,
  useUpdateProgramMutation,
  useUserPartnerChoicesQuery,
} from '@generated/graphql';
import { ALL_LOG_ENTRIES_QUERY } from '../../../apollo/queries/core/AllLogEntries';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { DetailsStep } from '@components/programs/CreateProgram/DetailsStep';
import { PartnersStep } from '@components/programs/CreateProgram/PartnersStep';
import { programValidationSchema } from '@components/programs/CreateProgram/programValidationSchema';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import { decodeIdString } from '@utils/utils';
import { BreadCrumbsItem } from '@components/core/BreadCrumbs';
import { hasPermissionInModule } from '../../../config/permissions';
import { usePermissions } from '@hooks/usePermissions';

export const EditProgramPage = (): ReactElement => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { id } = useParams();
  const permissions = usePermissions();

  const [step, setStep] = useState(0);
  const { showMessage } = useSnackbar();
  const { baseUrl, businessArea } = useBaseUrl();
  const { data: treeData, loading: treeLoading } = useAllAreasTreeQuery({
    variables: { businessArea },
  });
  const { data, loading: loadingProgram } = useProgramQuery({
    variables: { id },
    fetchPolicy: 'cache-and-network',
  });
  const { data: userPartnerChoicesData, loading: userPartnerChoicesLoading } =
    useUserPartnerChoicesQuery();

  const [mutate] = useUpdateProgramMutation({
    refetchQueries: [
      {
        query: ALL_LOG_ENTRIES_QUERY,
        variables: {
          objectId: decodeIdString(id),
          count: 5,
          businessArea,
        },
      },
    ],
  });

  if (loadingProgram || treeLoading || userPartnerChoicesLoading)
    return <LoadingComponent />;
  if (!data || !treeData || !userPartnerChoicesData) return null;
  const {
    name,
    programmeCode,
    startDate,
    endDate,
    sector,
    dataCollectingType,
    description,
    budget = '',
    administrativeAreasOfImplementation,
    populationGoal = '',
    cashPlus = false,
    frequencyOfPayments = 'REGULAR',
    version,
    partners,
    partnerAccess = ProgramPartnerAccess.AllPartnersAccess,
  } = data.program;

  const handleSubmit = async (values): Promise<void> => {
    delete values.editMode;
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
        ? values.partners.map(({ id: partnerId, areas, areaAccess }) => ({
            partner: partnerId,
            areas: areaAccess === 'ADMIN_AREA' ? areas : [],
            areaAccess,
          }))
        : [];

    try {
      const response = await mutate({
        variables: {
          programData: {
            id,
            ...values,
            budget: budgetToFixed,
            populationGoal: populationGoalParsed,
            partners: partnersToSet,
          },
          version,
        },
      });
      showMessage(t('Programme edited.'));
      navigate(`/${baseUrl}/details/${response.data.updateProgram.program.id}`);
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
    }
  };

  const initialValues = {
    editMode: true,
    name,
    programmeCode,
    startDate,
    endDate,
    sector,
    dataCollectingTypeCode: dataCollectingType?.code,
    description,
    budget,
    administrativeAreasOfImplementation,
    populationGoal,
    cashPlus,
    frequencyOfPayments,
    partners: partners
      .filter((partner) => partner.name !== 'UNICEF')
      .map((partner) => ({
        id: partner.id,
        areas: partner.areas.map((area) => decodeIdString(area.id)),
        areaAccess: partner.areaAccess,
      })),
    partnerAccess,
  };
  initialValues.budget =
    data.program.budget === '0.00' ? '' : data.program.budget;
  initialValues.populationGoal =
    data.program.populationGoal === 0 ? '' : data.program.populationGoal;

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

  const { allAreasTree } = treeData;
  const { userPartnerChoices } = userPartnerChoicesData;

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Programme'),
      to: `/${baseUrl}/details/${id}`,
    },
  ];

  return (
    <Formik
      initialValues={initialValues}
      onSubmit={(values) => {
        handleSubmit(values);
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
              title={`${t('Edit Programme')}: (${name})`}
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
