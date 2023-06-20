import { FieldArray, Form, Formik } from 'formik';
import React from 'react';
import { useTranslation } from 'react-i18next';
import * as Yup from 'yup';
import styled from 'styled-components';
import { Typography } from '@material-ui/core';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { CreateTargetPopulationHeader } from '../../../components/targeting/CreateTargetPopulation/CreateTargetPopulationHeader';
import { Exclusions } from '../../../components/targeting/CreateTargetPopulation/Exclusions';
import { TargetingCriteria } from '../../../components/targeting/TargetingCriteria';
import { TargetingCriteriaDisabled } from '../../../components/targeting/TargetingCriteria/TargetingCriteriaDisabled';
import { TargetPopulationProgramme } from '../../../components/targeting/TargetPopulationProgramme';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { usePermissions } from '../../../hooks/usePermissions';
import { useSnackbar } from '../../../hooks/useSnackBar';
import { getTargetingCriteriaVariables } from '../../../utils/targetingUtils';
import { getFullNodeFromEdgesById } from '../../../utils/utils';
import {
  ProgramStatus,
  useAllProgramsForChoicesQuery,
  useBusinessAreaDataQuery,
  useCreateTpMutation,
} from '../../../__generated__/graphql';
import { PaperContainer } from '../../../components/targeting/PaperContainer';
import { AutoSubmitFormOnEnter } from '../../../components/core/AutoSubmitFormOnEnter';
import { useBaseUrl } from '../../../hooks/useBaseUrl';

const Label = styled.p`
  color: #b1b1b5;
`;

export const CreateTargetPopulationPage = (): React.ReactElement => {
  const { t } = useTranslation();
  const initialValues = {
    name: '',
    criterias: [],
    program: null,
    excludedIds: '',
    exclusionReason: '',
    flagExcludeIfActiveAdjudicationTicket: false,
    flagExcludeIfOnSanctionList: false,
  };
  const [mutate, { loading }] = useCreateTpMutation();
  const { showMessage } = useSnackbar();
  const { baseUrl, businessArea } = useBaseUrl();
  const permissions = usePermissions();

  const { data: businessAreaData } = useBusinessAreaDataQuery({
    variables: { businessAreaSlug: businessArea },
  });

  const {
    data: allProgramsData,
    loading: loadingPrograms,
  } = useAllProgramsForChoicesQuery({
    variables: { businessArea, status: [ProgramStatus.Active] },
    fetchPolicy: 'network-only',
  });

  if (loadingPrograms) return <LoadingComponent />;
  if (permissions === null) return null;
  if (!allProgramsData || !businessAreaData) return null;
  if (!hasPermissions(PERMISSIONS.TARGETING_CREATE, permissions))
    return <PermissionDenied />;

  const validationSchema = Yup.object().shape({
    name: Yup.string()
      .min(2, t('Too short'))
      .max(255, t('Too long')),
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
      const res = await mutate({
        variables: {
          input: {
            programId: values.program,
            name: values.name,
            excludedIds: values.excludedIds,
            exclusionReason: values.exclusionReason,
            businessAreaSlug: businessArea,
            ...getTargetingCriteriaVariables(values),
          },
        },
      });
      showMessage(t('Target Population Created'), {
        pathname: `/${baseUrl}/target-population/${res.data.createTargetPopulation.targetPopulation.id}`,
        historyMethod: 'push',
      });
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
    }
  };

  return (
    <Formik
      initialValues={initialValues}
      validationSchema={validationSchema}
      onSubmit={handleSubmit}
    >
      {({ submitForm, values, setFieldValue }) => (
        <Form>
          <AutoSubmitFormOnEnter />
          <CreateTargetPopulationHeader
            handleSubmit={submitForm}
            loading={loading}
            values={values}
            baseUrl={baseUrl}
            permissions={permissions}
          />
          <TargetPopulationProgramme
            allPrograms={allProgramsData}
            loading={loadingPrograms}
            program={values.program}
            setFieldValue={setFieldValue}
            values={values}
          />
          {values.program ? (
            <FieldArray
              name='criterias'
              render={(arrayHelpers) => (
                <TargetingCriteria
                  helpers={arrayHelpers}
                  rules={values.criterias}
                  selectedProgram={getFullNodeFromEdgesById(
                    allProgramsData?.allPrograms?.edges,
                    values.program,
                  )}
                  screenBeneficiary={
                    businessAreaData?.businessArea?.screenBeneficiary
                  }
                  isEdit
                />
              )}
            />
          ) : (
            <TargetingCriteriaDisabled />
          )}
          <Exclusions />
          <PaperContainer>
            <Typography variant='h6'>
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
};
