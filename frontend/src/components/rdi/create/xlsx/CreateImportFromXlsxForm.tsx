/* eslint-disable react-hooks/exhaustive-deps */
import { Box, CircularProgress } from '@mui/material';
import { Field, FormikProvider, useFormik } from 'formik';
import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import * as Yup from 'yup';
import {
  ImportDataStatus,
  useCreateRegistrationXlsxImportMutation,
  useProgramQuery,
} from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { ScreenBeneficiaryField } from '../ScreenBeneficiaryField';
import { DropzoneField } from './DropzoneField';
import { XlsxImportDataRepresentation } from './XlsxImportDataRepresentation';
import { useSaveXlsxImportDataAndCheckStatus } from './useSaveXlsxImportDataAndCheckStatus';

const CircularProgressContainer = styled.div`
  display: flex;
  justify-content: center;
  align-content: center;
  height: 50px;
  width: 100%;
`;

const validationSchema = Yup.object().shape({
  name: Yup.string()
    .required('Title is required')
    .min(4, 'Too short')
    .max(255, 'Too long'),
});
export function CreateImportFromXlsxForm({
  setSubmitForm,
  setSubmitDisabled,
}): React.ReactElement {
  const {
    saveAndStartPolling,
    stopPollingImportData,
    loading: saveXlsxLoading,
    xlsxImportData,
  } = useSaveXlsxImportDataAndCheckStatus();
  const { baseUrl, businessArea, programId } = useBaseUrl();
  const { showMessage } = useSnackbar();
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [createImport] = useCreateRegistrationXlsxImportMutation();
  const { data: programData } = useProgramQuery({
    variables: { id: programId },
  });

  const onSubmit = async (values): Promise<void> => {
    setSubmitDisabled(true);
    try {
      const data = await createImport({
        variables: {
          registrationDataImportData: {
            importDataId: xlsxImportData.id,
            name: values.name,
            screenBeneficiary: values.screenBeneficiary,
            businessAreaSlug: businessArea,
          },
        },
      });
      if (programData.program.isSocialWorkerProgram) {
        navigate(
          `/${baseUrl}/registration-data-import-for-people/${data.data.registrationXlsxImport.registrationDataImport.id}`,
        );
      } else {
        navigate(
          `/${baseUrl}/registration-data-import/${data.data.registrationXlsxImport.registrationDataImport.id}`,
        );
      }
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
      setSubmitDisabled(false);
    }
  };

  const formik = useFormik({
    initialValues: {
      name: '',
      screenBeneficiary: false,
      file: null,
    },
    validationSchema,
    onSubmit,
  });
  // eslint-disable-next-line @typescript-eslint/require-await
  const saveXlsxInputData = async (): Promise<void> => {
    if (!formik.values.file) {
      return;
    }
    setSubmitDisabled(true);
    stopPollingImportData();
    await saveAndStartPolling({
      businessAreaSlug: businessArea,
      file: formik.values.file,
    });
  };
  useEffect(() => stopPollingImportData, []);
  useEffect(() => {
    saveXlsxInputData();
  }, [formik.values.file]);
  useEffect(() => {
    setSubmitForm(formik.submitForm);
  }, [formik.submitForm]);
  useEffect(() => {
    if (xlsxImportData?.status === ImportDataStatus.Finished) {
      setSubmitDisabled(false);
    }
  }, [xlsxImportData]);

  return (
    <FormikProvider value={formik}>
      <DropzoneField loading={saveXlsxLoading} />
      <Box mt={2}>
        <Field
          name="name"
          fullWidth
          label={t('Title')}
          required
          variant="outlined"
          component={FormikTextField}
        />
      </Box>
      <ScreenBeneficiaryField />
      {saveXlsxLoading ? (
        <CircularProgressContainer>
          <CircularProgress />
        </CircularProgressContainer>
      ) : (
        <XlsxImportDataRepresentation
          xlsxImportData={xlsxImportData}
          loading={saveXlsxLoading}
        />
      )}
    </FormikProvider>
  );
}
