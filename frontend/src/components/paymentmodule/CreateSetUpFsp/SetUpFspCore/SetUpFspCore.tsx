import { Box } from '@material-ui/core';
import Step from '@material-ui/core/Step';
import StepLabel from '@material-ui/core/StepLabel';
import Stepper from '@material-ui/core/Stepper';
import { FieldArray, Form, Formik } from 'formik';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useParams } from 'react-router-dom';
import { useSnackbar } from '../../../../hooks/useSnackBar';
import {
  AvailableFspsForDeliveryMechanismsDocument,
  PaymentPlanDocument,
  useAllDeliveryMechanismsQuery,
  useAssignFspToDeliveryMechMutation,
  useAvailableFspsForDeliveryMechanismsQuery,
  useChooseDeliveryMechForPaymentPlanMutation,
} from '../../../../__generated__/graphql';
import { AutoSubmitFormOnEnter } from '../../../core/AutoSubmitFormOnEnter';
import { ContainerColumnWithBorder } from '../../../core/ContainerColumnWithBorder';
import { LoadingComponent } from '../../../core/LoadingComponent';
import { DeliveryMechanismRow } from '../DeliveryMechanismRow';
import { SetUpFspButtonActions } from '../SetUpFspButtonActions/SetUpFspButtonActions';

export interface FormValues {
  deliveryMechanisms: {
    deliveryMechanism: string;
    fsp: string;
  }[];
}

interface SetUpFspCoreProps {
  businessArea: string;
  permissions: string[];
  initialValues: FormValues;
}

export const SetUpFspCore = ({
  businessArea,
  permissions,
  initialValues,
}: SetUpFspCoreProps): React.ReactElement => {
  const { t } = useTranslation();
  const { id } = useParams();
  const location = useLocation();

  const {
    data: deliveryMechanismsData,
    loading: deliveryMechanismLoading,
  } = useAllDeliveryMechanismsQuery({
    fetchPolicy: 'network-only',
  });

  const { data: fspsData } = useAvailableFspsForDeliveryMechanismsQuery({
    variables: {
      input: {
        paymentPlanId: id,
      },
    },
    fetchPolicy: 'network-only',
  });

  const isEdit = location.pathname.indexOf('edit') !== -1;

  const [activeStep, setActiveStep] = useState(isEdit ? 1 : 0);
  // const [warning, setWarning] = useState('');

  const [
    chooseDeliveryMechanisms,
  ] = useChooseDeliveryMechForPaymentPlanMutation();

  const [assignFspToDeliveryMechanism] = useAssignFspToDeliveryMechMutation();

  const { showMessage } = useSnackbar();

  if (!deliveryMechanismsData) return null;
  if (deliveryMechanismLoading) return <LoadingComponent />;

  const steps = [
    t('Choose Delivery Mechanism'),
    t('Assign FSP per Delivery Mechanism'),
  ];

  const handleBackStep = (): void => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const handleNextStep = (): void => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };

  const handleChooseDeliveryMechanisms = async (
    values: FormValues,
  ): Promise<void> => {
    // setWarning('');
    const mappedDeliveryMechanisms = values.deliveryMechanisms.map(
      (el) => el.deliveryMechanism,
    );
    try {
      await chooseDeliveryMechanisms({
        variables: {
          input: {
            paymentPlanId: id,
            deliveryMechanisms: mappedDeliveryMechanisms,
          },
        },
        refetchQueries: () => [
          {
            query: AvailableFspsForDeliveryMechanismsDocument,
            variables: {
              input: {
                paymentPlanId: id,
              },
            },
          },
          {
            query: PaymentPlanDocument,
            variables: {
              id,
            },
          },
        ],
      });

      showMessage(t('Delivery Mechanisms have been set'));
      handleNextStep();
    } catch (e) {
      // if (
      //   e.graphQLErrors.length &&
      //   e.graphQLErrors[0]?.message.includes('sufficient')
      // ) {
      //   setWarning(e.graphQLErrors[0].message);
      // }
      e.graphQLErrors.map((x) => showMessage(x.message));
    }
  };

  const handleAssignFspToDeliveryMechanism = async (
    values: FormValues,
  ): Promise<void> => {
    const mappings = values.deliveryMechanisms.map((el, index) => ({
      fspId: el.fsp,
      deliveryMechanism: el.deliveryMechanism,
      order: index + 1,
    }));
    try {
      await assignFspToDeliveryMechanism({
        variables: {
          input: {
            paymentPlanId: id,
            mappings,
          },
        },
      });
      showMessage(t('FSPs have been assigned to the delivery mechanisms'), {
        pathname: `/${businessArea}/payment-module/payment-plans/${id}`,
        historyMethod: 'push',
      });
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
    }
  };

  const handleSubmit = (values: FormValues): void => {
    if (activeStep === 0) {
      handleChooseDeliveryMechanisms(values);
    }
    if (activeStep === 1) {
      handleAssignFspToDeliveryMechanism(values);
    }
  };

  return (
    <Formik
      initialValues={initialValues}
      onSubmit={(values) => handleSubmit(values)}
      enableReinitialize
    >
      {({ values, submitForm }) => {
        const checkFspIsEmpty = (obj): boolean => {
          for (let i = 0; i < obj.deliveryMechanisms.length; i + 1) {
            if (obj.deliveryMechanisms[i].fsp === '') {
              return true;
            }
          }
          return false;
        };

        const isFspEmpty = checkFspIsEmpty(values);

        return (
          <Form>
            <AutoSubmitFormOnEnter />
            <Box m={5}>
              <ContainerColumnWithBorder>
                <Box>
                  <Stepper activeStep={activeStep}>
                    {steps.map((step) => {
                      return (
                        <Step key={step}>
                          <StepLabel>{step}</StepLabel>
                        </Step>
                      );
                    })}
                  </Stepper>
                </Box>
                {/* // warning not shown in Payment Module 1.0 */}
                {/* {warning && <DeliveryMechanismWarning warning={warning} />} */}
                <FieldArray
                  name='deliveryMechanisms'
                  render={(arrayHelpers) => {
                    return (
                      <>
                        {values.deliveryMechanisms.map(
                          (item, index: number) => {
                            const mapping =
                              fspsData?.availableFspsForDeliveryMechanisms[
                                index
                              ];
                            const mappedFsps = mapping?.fsps.map((el) => ({
                              name: el.name,
                              value: el.id,
                            }));

                            const deliveryMechanismsChoices = deliveryMechanismsData.allDeliveryMechanisms.map(
                              (el) => ({
                                name: el.name,
                                value: el.value,
                              }),
                            );

                            return (
                              <DeliveryMechanismRow
                                /* eslint-disable-next-line react/no-array-index-key */
                                key={`${item.deliveryMechanism}-${index}`}
                                index={index}
                                arrayHelpers={arrayHelpers}
                                deliveryMechanismsChoices={
                                  deliveryMechanismsChoices
                                }
                                fspsChoices={mappedFsps}
                                step={activeStep}
                                values={values}
                                permissions={permissions}
                              />
                            );
                          },
                        )}
                        {/* // button not shown in Payment Module 1.0 */}
                        {/* {activeStep === 0 && (
                          <Grid container>
                            <Grid item xs={12}>
                              <Box pt={3}>
                                <Button
                                  color='primary'
                                  startIcon={<AddCircleOutline />}
                                  onClick={() => {
                                    arrayHelpers.push({
                                      deliveryMechanism: '',
                                      fsp: '',
                                    });
                                  }}
                                  data-cy='button-add-delivery-mechanism'
                                >
                                  {t('Add Delivery Mechanism')}
                                </Button>
                              </Box>
                            </Grid>
                          </Grid>
                        )} */}
                      </>
                    );
                  }}
                />
                <SetUpFspButtonActions
                  step={activeStep}
                  submitForm={submitForm}
                  businessArea={businessArea}
                  paymentPlanId={id}
                  handleBackStep={handleBackStep}
                  isFspEmpty={isFspEmpty}
                />
              </ContainerColumnWithBorder>
            </Box>
          </Form>
        );
      }}
    </Formik>
  );
};
