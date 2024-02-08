import { Typography } from '@mui/material';
import { FieldArray, Form, Formik } from 'formik';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import * as Yup from 'yup';
import {
  ProgramStatus,
  TargetPopulationQuery,
  TargetPopulationStatus,
  useAllProgramsForChoicesQuery,
  useUpdateTpMutation,
} from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import { getTargetingCriteriaVariables } from '@utils/targetingUtils';
import { getFullNodeFromEdgesById } from '@utils/utils';
import { AutoSubmitFormOnEnter } from '@core/AutoSubmitFormOnEnter';
import { LoadingComponent } from '@core/LoadingComponent';
import { Exclusions } from '../CreateTargetPopulation/Exclusions';
import { PaperContainer } from '../PaperContainer';
import { TargetingCriteria } from '../TargetingCriteria';
import { EditTargetPopulationHeader } from './EditTargetPopulationHeader';

const Label = styled.p`
  color: #b1b1b5;
`;

interface EditTargetPopulationProps {
  targetPopulation: TargetPopulationQuery['targetPopulation'];
  screenBeneficiary: boolean;
}

export function EditTargetPopulation({
  targetPopulation,
  screenBeneficiary,
}: EditTargetPopulationProps): React.ReactElement {
  const { t } = useTranslation();
  const initialValues = {
    id: targetPopulation.id,
    name: targetPopulation.name || '',
    program: targetPopulation.program?.id || '',
    targetingCriteria: targetPopulation.targetingCriteria.rules || [],
    excludedIds: targetPopulation.excludedIds || '',
    exclusionReason: targetPopulation.exclusionReason || '',
    flagExcludeIfActiveAdjudicationTicket:
      targetPopulation.targetingCriteria
        .flagExcludeIfActiveAdjudicationTicket || false,
    flagExcludeIfOnSanctionList:
      targetPopulation.targetingCriteria.flagExcludeIfOnSanctionList || false,
  };
  const [mutate, { loading }] = useUpdateTpMutation();
  const { showMessage } = useSnackbar();
  const { baseUrl, businessArea } = useBaseUrl();
  const { data: allProgramsData, loading: loadingPrograms } =
    useAllProgramsForChoicesQuery({
      variables: { businessArea, status: [ProgramStatus.Active] },
      fetchPolicy: 'cache-and-network',
    });

  if (loadingPrograms) {
    return <LoadingComponent />;
  }
  if (!allProgramsData) {
    return null;
  }

  const handleValidate = (values): { targetingCriteria?: string } => {
    const { targetingCriteria } = values;
    const errors: { targetingCriteria?: string } = {};
    if (!targetingCriteria.length) {
      errors.targetingCriteria = t(
        'You need to select at least one targeting criteria',
      );
    }
    return errors;
  };
  const validationSchema = Yup.object().shape({
    name: Yup.string()
      .min(3, 'Targeting name should have at least 3 characters.')
      .max(255, 'Targeting name should have at most 255 characters.'),
    excludedIds: Yup.string().test(
      'testName',
      'ID is not in the correct format',
      (ids) => {
        if (!ids?.length) {
          return true;
        }
        const idsArr = ids.split(',');
        return idsArr.every((el) =>
          /^\s*(IND|HH)-\d{2}-\d{4}\.\d{4}\s*$/.test(el),
        );
      },
    ),
    exclusionReason: Yup.string().max(500, t('Too long')),
  });

  const handleSubmit = async (values): Promise<void> => {
    try {
      await mutate({
        variables: {
          input: {
            id: values.id,
            programId: values.program,
            excludedIds: values.excludedIds,
            exclusionReason: values.exclusionReason,
            ...(targetPopulation.status === TargetPopulationStatus.Open && {
              name: values.name,
            }),
            ...getTargetingCriteriaVariables({
              flagExcludeIfActiveAdjudicationTicket:
                values.flagExcludeIfActiveAdjudicationTicket,
              flagExcludeIfOnSanctionList: values.flagExcludeIfOnSanctionList,
              criterias: values.targetingCriteria,
            }),
          },
        },
      });
      showMessage(t('Target Population Updated'), {
        pathname: `/${baseUrl}/target-population/${values.id}`,
        historyMethod: 'push',
      });
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
    }
  };

  const selectedProgram = (values): void =>
    getFullNodeFromEdgesById(
      allProgramsData?.allPrograms?.edges,
      values.program,
    );

  return (
    <Formik
      initialValues={initialValues}
      validate={handleValidate}
      validationSchema={validationSchema}
      onSubmit={handleSubmit}
    >
      {({ values, submitForm }) => (
        <Form>
          <AutoSubmitFormOnEnter />
          <EditTargetPopulationHeader
            handleSubmit={submitForm}
            values={values}
            loading={loading}
            baseUrl={baseUrl}
            targetPopulation={targetPopulation}
          />
          <FieldArray
            name="targetingCriteria"
            render={(arrayHelpers) => (
              <TargetingCriteria
                helpers={arrayHelpers}
                rules={values.targetingCriteria}
                selectedProgram={selectedProgram(values)}
                isEdit
                screenBeneficiary={screenBeneficiary}
              />
            )}
          />
          <Exclusions initialOpen={Boolean(values.excludedIds)} />
          <PaperContainer>
            <Typography variant="h6">
              {t('Save to see the list of households')}
            </Typography>
            <Label>
              {t('List of households will be available after saving')}
            </Label>
          </PaperContainer>
        </Form>
      )}
    </Formik>
  );
}
