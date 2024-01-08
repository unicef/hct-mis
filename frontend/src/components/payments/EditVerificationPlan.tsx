import {
  Box,
  Button,
  DialogContent,
  DialogTitle,
  Grid,
  Tab,
  Tabs,
  Typography,
} from '@material-ui/core';
import EditIcon from '@material-ui/icons/EditRounded';
import { Field, Form, Formik } from 'formik';
import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { useHistory } from 'react-router-dom';
import {
  PaymentPlanQuery,
  useAllAdminAreasQuery,
  useAllRapidProFlowsLazyQuery,
  useEditPaymentVerificationPlanMutation,
  useSampleSizeLazyQuery,
} from '../../__generated__/graphql';
import { Dialog } from '../../containers/dialogs/Dialog';
import { DialogActions } from '../../containers/dialogs/DialogActions';
import { DialogContainer } from '../../containers/dialogs/DialogContainer';
import { DialogFooter } from '../../containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '../../containers/dialogs/DialogTitleWrapper';
import { useBaseUrl } from '../../hooks/useBaseUrl';
import { usePaymentRefetchQueries } from '../../hooks/usePaymentRefetchQueries';
import { useSnackbar } from '../../hooks/useSnackBar';
import { useProgramContext } from '../../programContext';
import { FormikCheckboxField } from '../../shared/Formik/FormikCheckboxField';
import { FormikMultiSelectField } from '../../shared/Formik/FormikMultiSelectField';
import { FormikRadioGroup } from '../../shared/Formik/FormikRadioGroup';
import { FormikSelectField } from '../../shared/Formik/FormikSelectField';
import { FormikSliderField } from '../../shared/Formik/FormikSliderField';
import { FormikTextField } from '../../shared/Formik/FormikTextField';
import { AutoSubmitFormOnEnter } from '../core/AutoSubmitFormOnEnter';
import { FormikEffect } from '../core/FormikEffect';
import { LoadingButton } from '../core/LoadingButton';
import { TabPanel } from '../core/TabPanel';

const StyledTabs = styled(Tabs)`
  && {
    max-width: 500px;
  }
`;
const TabsContainer = styled.div`
  border-bottom: 1px solid #e8e8e8;
`;

// eslint-disable-next-line @typescript-eslint/explicit-function-return-type
function prepareVariables(
  cashOrPaymentPlanId = null,
  paymentVerificationPlanId,
  selectedTab,
  values,
  businessArea,
) {
  return {
    input: {
      ...(cashOrPaymentPlanId && {
        cashOrPaymentPlanId,
      }),
      ...(paymentVerificationPlanId && {
        paymentVerificationPlanId,
      }),
      sampling: selectedTab === 0 ? 'FULL_LIST' : 'RANDOM',
      fullListArguments:
        selectedTab === 0
          ? {
              excludedAdminAreas: values.excludedAdminAreasFull || [],
            }
          : null,
      verificationChannel: values.verificationChannel,
      rapidProArguments:
        values.verificationChannel === 'RAPIDPRO'
          ? {
              flowId: values.rapidProFlow,
            }
          : null,
      randomSamplingArguments:
        selectedTab === 1
          ? {
              confidenceInterval: values.confidenceInterval * 0.01,
              marginOfError: values.marginOfError * 0.01,
              excludedAdminAreas: values.adminCheckbox
                ? values.excludedAdminAreasRandom
                : [],
              age: values.ageCheckbox
                ? {
                    min: values.filterAgeMin || null,
                    max: values.filterAgeMax || null,
                  }
                : null,
              sex: values.sexCheckbox ? values.filterSex : null,
            }
          : null,
      businessAreaSlug: businessArea,
    },
  };
}

export interface Props {
  paymentVerificationPlanNode: PaymentPlanQuery['paymentPlan']['verificationPlans']['edges'][0]['node'];
  cashOrPaymentPlanId: string;
}

export function EditVerificationPlan({
  paymentVerificationPlanNode,
  cashOrPaymentPlanId,
}: Props): React.ReactElement {
  const refetchQueries = usePaymentRefetchQueries(cashOrPaymentPlanId);
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const [selectedTab, setSelectedTab] = useState(0);
  const { showMessage } = useSnackbar();
  const [mutate, { loading }] = useEditPaymentVerificationPlanMutation();
  const { businessArea } = useBaseUrl();
  const { isActiveProgram } = useProgramContext();
  const history = useHistory();

  useEffect(() => {
    if (paymentVerificationPlanNode.sampling === 'FULL_LIST') {
      setSelectedTab(0);
    } else {
      setSelectedTab(1);
    }
  }, [paymentVerificationPlanNode.sampling]);

  const initialValues = {
    confidenceInterval:
      paymentVerificationPlanNode.confidenceInterval * 100 || 95,
    marginOfError: paymentVerificationPlanNode.marginOfError * 100 || 5,
    filterAgeMin: paymentVerificationPlanNode.ageFilter?.min || '',
    filterAgeMax: paymentVerificationPlanNode.ageFilter?.max || '',
    filterSex: paymentVerificationPlanNode.sexFilter || '',
    excludedAdminAreasFull:
      paymentVerificationPlanNode.excludedAdminAreasFilter || [],
    excludedAdminAreasRandom:
      paymentVerificationPlanNode.excludedAdminAreasFilter || [],
    verificationChannel:
      paymentVerificationPlanNode.verificationChannel || null,
    rapidProFlow: paymentVerificationPlanNode.rapidProFlowId || '',
    adminCheckbox:
      paymentVerificationPlanNode.excludedAdminAreasFilter?.length !== 0,
    ageCheckbox:
      Boolean(paymentVerificationPlanNode.ageFilter?.min) ||
      Boolean(paymentVerificationPlanNode.ageFilter?.max) ||
      false,
    sexCheckbox: Boolean(paymentVerificationPlanNode.sexFilter) || false,
  };

  const [formValues, setFormValues] = useState(initialValues);

  const [
    loadRapidProFlows,
    { data: rapidProFlows },
  ] = useAllRapidProFlowsLazyQuery({
    variables: {
      businessAreaSlug: businessArea,
    },
  });
  const { data } = useAllAdminAreasQuery({
    variables: {
      first: 100,
      businessArea,
    },
  });

  const [loadSampleSize, { data: sampleSizesData }] = useSampleSizeLazyQuery({
    variables: prepareVariables(
      cashOrPaymentPlanId,
      paymentVerificationPlanNode.id,
      selectedTab,
      formValues,
      businessArea,
    ),
    fetchPolicy: 'network-only',
  });

  useEffect(() => {
    if (open) {
      loadSampleSize();
      if (formValues.verificationChannel === 'RAPIDPRO') {
        loadRapidProFlows();
      }
    }
  }, [formValues, open, loadSampleSize, loadRapidProFlows]);

  const submit = async (values): Promise<void> => {
    const { errors } = await mutate({
      variables: prepareVariables(
        null,
        paymentVerificationPlanNode.id,
        selectedTab,
        values,
        businessArea,
      ),
      refetchQueries,
    });
    setOpen(false);

    if (errors) {
      showMessage(t('Error while submitting'));
      return;
    }
    showMessage(t('Verification plan edited.'));
  };

  const mappedAdminAreas = data?.allAdminAreas?.edges?.length
    ? data.allAdminAreas.edges.map((el) => ({
        value: el.node.id,
        name: el.node.name,
      }))
    : [];

  const handleFormChange = (values): void => {
    setFormValues(values);
  };

  const getSampleSizePercentage = (): string => {
    if (sampleSizesData?.sampleSize?.paymentRecordCount !== 0) {
      return ` (${(sampleSizesData?.sampleSize?.sampleSize /
        sampleSizesData?.sampleSize?.paymentRecordCount) *
        100})%`;
    }
    return ` (0%)`;
  };
  return (
    <Formik initialValues={initialValues} onSubmit={submit}>
      {({ submitForm, values, setValues }) => {
        //Redirect to error page if no flows available
        if (
          !rapidProFlows?.allRapidProFlows?.length &&
          values.verificationChannel === 'RAPIDPRO'
        ) {
          history.push(`/error/${businessArea}`, {
            errorMessage: t(
              'RapidPro is not set up in your country, please contact your Roll Out Focal Point',
            ),
            shouldGoBack: 'true',
          });
        }
        return (
          <Form>
            <AutoSubmitFormOnEnter />
            <FormikEffect
              values={values}
              onChange={() => handleFormChange(values)}
            />
            <Button
              color='primary'
              onClick={() => setOpen(true)}
              startIcon={<EditIcon />}
              data-cy='button-new-plan'
              disabled={!isActiveProgram}
            >
              {t('Edit')}
            </Button>
            <Dialog
              open={open}
              onClose={() => setOpen(false)}
              scroll='paper'
              aria-labelledby='form-dialog-title'
              maxWidth='md'
            >
              <DialogTitleWrapper>
                <DialogTitle>{t('Edit Verification Plan')}</DialogTitle>
              </DialogTitleWrapper>
              <DialogContent>
                <DialogContainer>
                  <TabsContainer>
                    <StyledTabs
                      value={selectedTab}
                      onChange={(
                        event: React.ChangeEvent<{}>,
                        newValue: number,
                      ) => {
                        setValues(initialValues);
                        setFormValues(initialValues);
                        setSelectedTab(newValue);
                      }}
                      indicatorColor='primary'
                      textColor='primary'
                      variant='fullWidth'
                      aria-label='full width tabs example'
                    >
                      <Tab label={t('FULL LIST')} />
                      <Tab label={t('RANDOM SAMPLING')} />
                    </StyledTabs>
                  </TabsContainer>
                  <TabPanel value={selectedTab} index={0}>
                    {mappedAdminAreas && (
                      <Field
                        name='excludedAdminAreasFull'
                        choices={mappedAdminAreas}
                        variant='outlined'
                        label={t('Filter Out Administrative Level Areas')}
                        component={FormikMultiSelectField}
                      />
                    )}
                    <Box pt={3}>
                      <Box
                        pb={3}
                        pt={3}
                        fontSize={16}
                        fontWeight='fontWeightBold'
                      >
                        Sample size: {sampleSizesData?.sampleSize?.sampleSize}{' '}
                        out of {sampleSizesData?.sampleSize?.paymentRecordCount}
                        {getSampleSizePercentage()}
                      </Box>
                      <Box fontSize={12} color='#797979'>
                        {t('This option is recommended for RapidPro')}
                      </Box>
                      <Field
                        name='verificationChannel'
                        label={t('Verification Channel')}
                        style={{ flexDirection: 'row', alignItems: 'center' }}
                        choices={[
                          { value: 'RAPIDPRO', name: 'RAPIDPRO' },
                          { value: 'XLSX', name: 'XLSX' },
                          { value: 'MANUAL', name: 'MANUAL' },
                        ]}
                        component={FormikRadioGroup}
                        alignItems='center'
                      />
                      {values.verificationChannel === 'RAPIDPRO' && (
                        <Field
                          name='rapidProFlow'
                          label='RapidPro Flow'
                          style={{ width: '90%' }}
                          choices={
                            rapidProFlows
                              ? rapidProFlows.allRapidProFlows.map((flow) => ({
                                  value: flow.id,
                                  name: flow.name,
                                }))
                              : []
                          }
                          component={FormikSelectField}
                        />
                      )}
                    </Box>
                  </TabPanel>
                  <TabPanel value={selectedTab} index={1}>
                    <Box pt={3}>
                      <Field
                        name='confidenceInterval'
                        label={t('Confidence Interval')}
                        min={90}
                        max={99}
                        component={FormikSliderField}
                        suffix='%'
                      />
                      <Field
                        name='marginOfError'
                        label={t('Margin of Error')}
                        min={0}
                        max={9}
                        component={FormikSliderField}
                        suffix='%'
                      />
                      <Typography variant='caption'>
                        {t('Cluster Filters')}
                      </Typography>
                      <Box flexDirection='column' display='flex'>
                        <Box display='flex'>
                          <Field
                            name='adminCheckbox'
                            label={t('Administrative Level')}
                            component={FormikCheckboxField}
                          />
                          <Field
                            name='ageCheckbox'
                            label={t('Age of HoH')}
                            component={FormikCheckboxField}
                          />
                          <Field
                            name='sexCheckbox'
                            label={t('Gender of HoH')}
                            component={FormikCheckboxField}
                          />
                        </Box>
                        {values.adminCheckbox && (
                          <Field
                            name='excludedAdminAreasRandom'
                            choices={mappedAdminAreas}
                            variant='outlined'
                            label={t('Filter Out Administrative Level Areas')}
                            component={FormikMultiSelectField}
                          />
                        )}

                        <Grid container>
                          {values.ageCheckbox && (
                            <Grid item xs={12}>
                              <Grid container>
                                <Grid item xs={4}>
                                  <Field
                                    name='filterAgeMin'
                                    label={t('Minimum Age')}
                                    type='number'
                                    color='primary'
                                    component={FormikTextField}
                                  />
                                </Grid>
                                <Grid item xs={4}>
                                  <Field
                                    name='filterAgeMax'
                                    label={t('Maximum Age')}
                                    type='number'
                                    color='primary'
                                    component={FormikTextField}
                                  />
                                </Grid>
                              </Grid>
                            </Grid>
                          )}
                          {values.sexCheckbox && (
                            <Grid item xs={5}>
                              <Field
                                name='filterSex'
                                label={t('Gender')}
                                color='primary'
                                choices={[
                                  { value: 'FEMALE', name: t('Female') },
                                  { value: 'MALE', name: t('Male') },
                                ]}
                                component={FormikSelectField}
                              />
                            </Grid>
                          )}
                        </Grid>
                      </Box>

                      <Box
                        pb={3}
                        pt={3}
                        fontSize={16}
                        fontWeight='fontWeightBold'
                      >
                        Sample size: {sampleSizesData?.sampleSize?.sampleSize}{' '}
                        out of {sampleSizesData?.sampleSize?.paymentRecordCount}{' '}
                        {getSampleSizePercentage()}
                      </Box>
                      <Field
                        name='verificationChannel'
                        label='Verification Channel'
                        style={{ flexDirection: 'row' }}
                        choices={[
                          { value: 'RAPIDPRO', name: 'RAPIDPRO' },
                          { value: 'XLSX', name: 'XLSX' },
                          { value: 'MANUAL', name: 'MANUAL' },
                        ]}
                        component={FormikRadioGroup}
                      />
                      {values.verificationChannel === 'RAPIDPRO' && (
                        <Field
                          name='rapidProFlow'
                          label='RapidPro Flow'
                          style={{ width: '90%' }}
                          choices={
                            rapidProFlows ? rapidProFlows.allRapidProFlows : []
                          }
                          component={FormikSelectField}
                        />
                      )}
                    </Box>
                  </TabPanel>
                </DialogContainer>
              </DialogContent>
              <DialogFooter>
                <DialogActions>
                  <Button onClick={() => setOpen(false)}>{t('CANCEL')}</Button>
                  <LoadingButton
                    loading={loading}
                    type='submit'
                    color='primary'
                    variant='contained'
                    onClick={submitForm}
                    data-cy='button-submit'
                  >
                    {t('SAVE')}
                  </LoadingButton>
                </DialogActions>
              </DialogFooter>
            </Dialog>
          </Form>
        );
      }}
    </Formik>
  );
}
