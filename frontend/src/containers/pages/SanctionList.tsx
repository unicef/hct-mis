/* eslint-disable react-hooks/exhaustive-deps */
import React, { useCallback, useState } from 'react';
import styled from 'styled-components';
import * as Yup from 'yup';
import { useTranslation } from 'react-i18next';
import { Button, Typography, Box } from '@material-ui/core';
import { useDropzone } from 'react-dropzone';
import { Form, Formik } from 'formik';
import get from 'lodash/get';
import {
  UploadImportDataXlsxFileMutation,
  useCreateRegistrationXlsxImportMutation,
  useUploadImportDataXlsxFileMutation,
  XlsxRowErrorNode,
} from '../../__generated__/graphql';

import { Errors } from '../registration/import/errors/PlainErrors';
import { LoadingComponent } from '../../components/LoadingComponent';
import { useSnackbar } from '../../hooks/useSnackBar';
import { useBusinessArea } from '../../hooks/useBusinessArea';

const DialogTitleWrapper = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
`;

const DialogFooter = styled.div`
  padding: 12px 16px;
  margin: 0;
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  text-align: right;
`;

const DropzoneContainer = styled.div`
  width: 500px;
  height: 100px;
  background-color: rgba(2, 62, 144, 0.1);
  color: #023e90;
  font-size: 14px;
  font-weight: 500;
  letter-spacing: 0.5px;
  line-height: 16px;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: ${({ theme }) => theme.spacing(5)}px;
  cursor: pointer;

  ${({ disabled }) => (disabled ? 'filter: grayscale(100%);' : '')}
`;

const StyledDialogFooter = styled(DialogFooter)`
  && {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
  }
`;

function DropzoneField({ onChange, loading }): React.ReactElement {
  const onDrop = useCallback((acceptedFiles) => {
    onChange(acceptedFiles);
  }, []);
  const { getRootProps, getInputProps, acceptedFiles } = useDropzone({
    disabled: loading,
    accept: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    onDrop,
  });
  const acceptedFilename =
    acceptedFiles.length > 0 ? acceptedFiles[0].name : null;
  return (
    <Box display='flex' justifyContent='center' p={5}>
      <DropzoneContainer {...getRootProps()} disabled={loading}>
        <LoadingComponent isLoading={loading} absolute />
        <input {...getInputProps()} data-cy='rdi-file-input' />
        {acceptedFilename || 'UPLOAD FILE'}
      </DropzoneContainer>
    </Box>
  );
}

const validationSchema = Yup.object().shape({
  name: Yup.string().required('Name Upload is required'),
});

export function SanctionList(): React.ReactElement {
  const { showMessage } = useSnackbar();
  const businessArea = useBusinessArea();
  const [
    uploadMutate,
    { data: uploadData, loading: fileLoading },
  ] = useUploadImportDataXlsxFileMutation();
  const [
    createRegistrationXlsxMutate,
    { loading: createLoading },
  ] = useCreateRegistrationXlsxImportMutation();

  const { t } = useTranslation();
  const xlsxErrors: UploadImportDataXlsxFileMutation['uploadImportDataXlsxFile']['errors'] = get(
    uploadData,
    'uploadImportDataXlsxFile.errors',
  );
  let disabled = null;

  let importFile = null;
  disabled = !uploadData || createLoading;
  importFile = (
    <>
      <DropzoneField
        loading={fileLoading}
        onChange={(files) => {
          if (files.length === 0) {
            return;
          }
          const file = files[0];
          const fileSizeMB = file.size / (1024 * 1024);
          if (fileSizeMB > 200) {
            showMessage(
              `File size is to big. It should be under 200MB, File size is ${fileSizeMB}MB`,
            );
            return;
          }
          uploadMutate({
            variables: {
              file,
              businessAreaSlug: businessArea,
            },
          });
        }}
      />
      <Errors errors={xlsxErrors as XlsxRowErrorNode[]} />
    </>
  );

  return (
    <>
      <Formik
        validationSchema={validationSchema}
        onSubmit={async (values) => {
          try {
            let rdiId = null;
            const { data } = await createRegistrationXlsxMutate({
              variables: {
                registrationDataImportData: {
                  importDataId:
                    uploadData.uploadImportDataXlsxFile.importData.id,
                  businessAreaSlug: businessArea,
                },
              },
            });
            rdiId = data?.registrationXlsxImport?.registrationDataImport?.id;

            showMessage('The import was successful');
          } catch (error) {
            showMessage('Something went wrong.');
          }
        }}
        initialValues={{ name: '' }}
      >
        {({ submitForm }) => (
          <Form>
            <DialogTitleWrapper>
              <Typography variant='h6'>{t('Select File to Import')}</Typography>
            </DialogTitleWrapper>
            {importFile}

            <Box display='flex' justifyContent='center' p={3}>
              <Button
                type='submit'
                color='primary'
                variant='contained'
                disabled={disabled}
                onClick={() => {
                  submitForm();
                }}
                data-cy='button-import'
              >
                {t('IMPORT')}
              </Button>
            </Box>
          </Form>
        )}
      </Formik>
    </>
  );
}
