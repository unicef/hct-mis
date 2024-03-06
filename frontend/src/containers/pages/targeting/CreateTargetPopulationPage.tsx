
import { Typography } from '@material-ui/core';
import { FieldArray, Form, Formik } from 'formik';
import React from 'react';
import { useHistory } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import * as Yup from 'yup';
import {
  ProgramStatus,
  useAllProgramsForChoicesQuery,
  useBusinessAreaDataQuery,
  useCreateTpMutation,
} from '../../../__generated__/graphql';
import { AutoSubmitFormOnEnter } from '../../../components/core/AutoSubmitFormOnEnter';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { CreateTargetPopulationHeader } from '../../../components/targeting/CreateTargetPopulation/CreateTargetPopulationHeader';
import { Exclusions } from '../../../components/targeting/CreateTargetPopulation/Exclusions';
import { PaperContainer } from '../../../components/targeting/PaperContainer';
import { TargetingCriteria } from '../../../components/targeting/TargetingCriteria';
import { TargetingCriteriaDisabled } from '../../../components/targeting/TargetingCriteria/TargetingCriteriaDisabled';
import { PERMISSIONS, hasPermissions } from '../../../config/permissions';
import { useBaseUrl } from '../../../hooks/useBaseUrl';
import { usePermissions } from '../../../hooks/usePermissions';
import { useSnackbar } from '../../../hooks/useSnackBar';
import { getTargetingCriteriaVariables } from '../../../utils/targetingUtils';
import { getFullNodeFromEdgesById } from '../../../utils/utils';

const Label = styled.p`
  color: #b1b1b5;
`;

export const CreateTargetPopulationPage = (): React.ReactElement => {
  const { t } = useTranslation();
  const { programId } = useBaseUrl();
  const initialValues = {
    name: '',
    criterias: [],
    program: programId,
    excludedIds: '',
    exclusionReason: '',
    flagExcludeIfActiveAdjudicationTicket: false,
    flagExcludeIfOnSanctionList: false,
  };
  const [mutate, { loading }] = useCreateTpMutation();
  const { showMessage } = useSnackbar();
  const { baseUrl, businessArea } = useBaseUrl();
  const permissions = usePermissions();
  const history = useHistory();

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
      .min(3, t('Targeting name should have at least 3 characters.'))
      .max(255, t('Targeting name should have at most 255 characters.')),
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
      showMessage(t('Target Population Created'));
      history.push(
        `/${baseUrl}/target-population/${res.data.createTargetPopulation.targetPopulation.id}`,
      );
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
      {({ submitForm, values }) => (
        <Form>
          <AutoSubmitFormOnEnter />
          <CreateTargetPopulationHeader
            handleSubmit={submitForm}
            loading={loading}
            values={values}
            baseUrl={baseUrl}
            permissions={permissions}
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
