import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogTitle,
} from '@material-ui/core';
import { Publish } from '@material-ui/icons';
import get from 'lodash/get';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { DialogTitleWrapper } from '../../../../containers/dialogs/DialogTitleWrapper';
import { ImportErrors } from '../../../../containers/tables/payments/VerificationRecordsTable/errors/ImportErrors';
import { useSnackbar } from '../../../../hooks/useSnackBar';
import {
  ImportXlsxPpListPerFspMutation,
  PaymentPlanBackgroundActionStatus,
  PaymentPlanDocument,
  PaymentPlanQuery,
  ProgramStatus,
  useImportXlsxPpListPerFspMutation,
} from '../../../../__generated__/graphql';
import { DropzoneField } from '../../../core/DropzoneField';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { useProgramContext } from "../../../../programContext";

const Error = styled.div`
  color: ${({ theme }) => theme.palette.error.dark};
  padding: 20px;
`;

const UploadIcon = styled(Publish)`
  color: #043f91;
`;

const DisabledUploadIcon = styled(Publish)`
  color: #00000042;
`;

interface ImportXlsxPaymentPlanPaymentListPerFspProps {
  paymentPlan: PaymentPlanQuery['paymentPlan'];
  permissions: string[];
}

const allowedState = [
  null,
  PaymentPlanBackgroundActionStatus.XlsxExportError,
  PaymentPlanBackgroundActionStatus.XlsxImportError,
  PaymentPlanBackgroundActionStatus.RuleEngineError,
];

export const ImportXlsxPaymentPlanPaymentListPerFsp = ({
  paymentPlan,
  permissions,
}: ImportXlsxPaymentPlanPaymentListPerFspProps): React.ReactElement => {
  const { showMessage } = useSnackbar();
  const [open, setOpenImport] = useState(false);
  const [fileToImport, setFileToImport] = useState(null);
  const { selectedProgram } = useProgramContext();
  const { t } = useTranslation();

  const [
    mutate,
    { data: uploadData, loading: fileLoading, error },
  ] = useImportXlsxPpListPerFspMutation();

  const xlsxErrors: ImportXlsxPpListPerFspMutation['importXlsxPaymentPlanPaymentListPerFsp']['errors'] = get(
    uploadData,
    'importXlsxPaymentPlanPaymentListPerFsp.errors',
  );
  const canUploadReconciliation =
    hasPermissions(
      PERMISSIONS.PM_IMPORT_XLSX_WITH_RECONCILIATION,
      permissions,
    ) && allowedState.includes(paymentPlan.backgroundActionStatus);

  const handleImport = async (): Promise<void> => {
    if (fileToImport) {
      try {
        const { data, errors } = await mutate({
          variables: {
            paymentPlanId: paymentPlan.id,
            file: fileToImport,
          },
          refetchQueries: () => [
            {
              query: PaymentPlanDocument,
              variables: {
                id: paymentPlan.id,
              },
            },
          ],
        });
        if (
          !errors &&
          !data?.importXlsxPaymentPlanPaymentListPerFsp.errors?.length
        ) {
          setOpenImport(false);
          showMessage(t('Your import was successful!'));
        }
      } catch (e) {
        e.graphQLErrors.map((x) => showMessage(x.message));
      }
    }
  };

  return (
    <>
      {canUploadReconciliation && (
        <Box key='import'>
          <Button
            startIcon={selectedProgram?.status !== ProgramStatus.Active ? <DisabledUploadIcon /> : <UploadIcon />}
            color='primary'
            data-cy='button-import'
            onClick={() => setOpenImport(true)}
            disabled={selectedProgram?.status !== ProgramStatus.Active}
          >
            {t('Upload Reconciliation Info')}
          </Button>
        </Box>
      )}
      <Dialog
        open={open}
        onClose={() => setOpenImport(false)}
        scroll='paper'
        aria-labelledby='form-dialog-title'
      >
        <DialogTitleWrapper data-cy='dialog-import'>
          <DialogTitle>{t('Select File to Import')}</DialogTitle>
          <>
            <DropzoneField
              dontShowFilename={false}
              loading={fileLoading}
              onChange={(files) => {
                if (files.length === 0) {
                  return;
                }
                const file = files[0];
                const fileSizeMB = file.size / (1024 * 1024);
                if (fileSizeMB > 200) {
                  showMessage(
                    `File size is too big. It should be under 200MB, File size is ${fileSizeMB}MB`,
                  );
                  return;
                }

                setFileToImport(file);
              }}
            />
            {fileToImport &&
            (error?.graphQLErrors?.length || xlsxErrors?.length) ? (
              <Error>
                <p>Errors</p>
                {error
                  ? error.graphQLErrors.map((x) => <p>{x.message}</p>)
                  : null}
                <ImportErrors errors={xlsxErrors} />
              </Error>
            ) : null}
          </>
          <DialogActions>
            <Button
              data-cy='close-button'
              onClick={() => {
                setOpenImport(false);
                setFileToImport(null);
              }}
            >
              CANCEL
            </Button>
            <Button
              disabled={!fileToImport}
              type='submit'
              color='primary'
              variant='contained'
              onClick={() => handleImport()}
              data-cy='button-import-submit'
            >
              {t('IMPORT')}
            </Button>
          </DialogActions>
        </DialogTitleWrapper>
      </Dialog>
    </>
  );
};
