import { Form, Formik } from 'formik';
import React from 'react';
import { useTranslation } from 'react-i18next';
import moment from 'moment';
import * as Yup from 'yup';
import { useHistory } from 'react-router-dom';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { CreatePaymentPlanHeader } from '../../../components/paymentmodule/CreatePaymentPlan/CreatePaymentPlanHeader/CreatePaymentPlanHeader';
import { PaymentPlanParameters } from '../../../components/paymentmodule/CreatePaymentPlan/PaymentPlanParameters';
import { PaymentPlanTargeting } from '../../../components/paymentmodule/CreatePaymentPlan/PaymentPlanTargeting/PaymentPlanTargeting';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { usePermissions } from '../../../hooks/usePermissions';
import { useSnackbar } from '../../../hooks/useSnackBar';
import {
  useAllTargetPopulationsQuery,
  useCreatePpMutation,
} from '../../../__generated__/graphql';
import { AutoSubmitFormOnEnter } from '../../../components/core/AutoSubmitFormOnEnter';
import { today } from '../../../utils/utils';
import { useBaseUrl } from '../../../hooks/useBaseUrl';

export const CreatePaymentPlanPage = (): React.ReactElement => {
  const history = useHistory();
  const { t } = useTranslation();
  const [mutate, { loading: loadingCreate }] = useCreatePpMutation();
  const { showMessage } = useSnackbar();
  const { baseUrl, businessArea, programId } = useBaseUrl();
  const permissions = usePermissions();

  const {
    data: allTargetPopulationsData,
    loading: loadingTargetPopulations,
  } = useAllTargetPopulationsQuery({
    variables: {
      businessArea,
      paymentPlanApplicable: true,
      program: [programId],
    },
    fetchPolicy: 'network-only',
  });

  if (loadingTargetPopulations) return <LoadingComponent />;
  if (!allTargetPopulationsData) return null;
  if (permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.PM_CREATE, permissions))
    return <PermissionDenied />;

  const validationSchema = Yup.object().shape({
    name: Yup.string()
      .required(t('Payment Plan Name is required'))
      .min(5, t('Too short'))
      .max(25, t('Too long')),
    targetingId: Yup.string().required(t('Target Population is required')),
    startDate: Yup.date().required(t('Start Date is required')),
    endDate: Yup.date()
      .required(t('End Date is required'))
      .when(
        'startDate',
        (startDate: string, schema) =>
          startDate &&
          schema.min(
            startDate,
            `${t('End date has to be greater than')} ${moment(startDate).format(
              'YYYY-MM-DD',
            )}`,
          ),
        '',
      ),
    currency: Yup.string()
      .nullable()
      .required(t('Currency is required')),
    dispersionStartDate: Yup.date().required(
      t('Dispersion Start Date is required'),
    ),
    dispersionEndDate: Yup.date()
      .required(t('Dispersion End Date is required'))
      .min(today, t('Dispersion End Date cannot be in the past'))
      .when(
        'dispersionStartDate',
        (dispersionStartDate: string, schema) =>
          dispersionStartDate &&
          schema.min(
            dispersionStartDate,
            `${t('Dispersion End Date has to be greater than')} ${moment(
              dispersionStartDate,
            ).format('YYYY-MM-DD')}`,
          ),
        '',
      ),
  });

  type FormValues = Yup.InferType<typeof validationSchema>;
  const initialValues: FormValues = {
    name: '',
    targetingId: '',
    startDate: '',
    endDate: '',
    currency: null,
    dispersionStartDate: '',
    dispersionEndDate: '',
  };
  const handleSubmit = async (values: FormValues): Promise<void> => {
    try {
      const res = await mutate({
        variables: {
          input: {
            businessAreaSlug: businessArea,
            ...values,
          },
        },
      });
      showMessage(t('Payment Plan Created'));
      history.push(
        `/${baseUrl}/payment-module/payment-plans/${res.data.createPaymentPlan.paymentPlan.id}`,
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
      validateOnChange
      validateOnBlur
    >
      {({ submitForm, values }) => (
        <Form>
          <AutoSubmitFormOnEnter />
          <CreatePaymentPlanHeader
            handleSubmit={submitForm}
            baseUrl={baseUrl}
            permissions={permissions}
            loadingCreate={loadingCreate}
          />
          <PaymentPlanTargeting
            allTargetPopulations={allTargetPopulationsData}
            loading={loadingTargetPopulations}
          />
          <PaymentPlanParameters values={values} />
        </Form>
      )}
    </Formik>
  );
};
