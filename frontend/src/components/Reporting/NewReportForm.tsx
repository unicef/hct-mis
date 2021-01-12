import React, { useState } from 'react';
import get from 'lodash/get';
import { Field, Form, Formik } from 'formik';
import {
  Button,
  DialogContent,
  DialogTitle,
  Typography,
  Paper,
  Grid,
} from '@material-ui/core';
import styled from 'styled-components';
import CalendarTodayRoundedIcon from '@material-ui/icons/CalendarTodayRounded';
import { Dialog } from '../../containers/dialogs/Dialog';
import { DialogActions } from '../../containers/dialogs/DialogActions';
import { useSnackbar } from '../../hooks/useSnackBar';
import { FormikSelectField } from '../../shared/Formik/FormikSelectField';
import { FormikDateField } from '../../shared/Formik/FormikDateField';
import {
  useAllProgramsQuery,
  useCreateReportMutation,
  useReportChoiceDataQuery,
} from '../../__generated__/graphql';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { LoadingComponent } from '../LoadingComponent';
import { FormikAdminAreaAutocomplete } from '../../shared/Formik/FormikAdminAreaAutocomplete';
import { ALL_REPORTS_QUERY } from '../../apollo/queries/AllReports';

const DialogTitleWrapper = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
`;

const DialogFooter = styled.div`
  padding: 12px 16px;
  margin: 0;
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  text-align: right;
`;

export const NewReportForm = (): React.ReactElement => {
  const [dialogOpen, setDialogOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const businessArea = useBusinessArea();
  const {
    data: allProgramsData,
    loading: loadingPrograms,
  } = useAllProgramsQuery({
    variables: { businessArea, status: ['ACTIVE'] },
  });
  const {
    data: choicesData,
    loading: choicesLoading,
  } = useReportChoiceDataQuery();
  const [mutate] = useCreateReportMutation();

  if (loadingPrograms || choicesLoading) return <LoadingComponent />;
  const allProgramsEdges = get(allProgramsData, 'allPrograms.edges', []);
  const mappedPrograms = allProgramsEdges.map((edge) => ({
    name: edge.node.name,
    value: edge.node.id,
  }));

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const initialValue: { [key: string]: any } = {
    reportType: '',
    dateFrom: '',
    dateTo: '',
    adminArea: '',
    program: '',
    country: '',
  };

  const submitFormHandler = async (values): Promise<void> => {
    console.log(values);
    const response = await mutate({
      variables: {
        reportData: {
          ...values,
          businessAreaSlug: businessArea,
        },
      },
      refetchQueries: () => [
        { query: ALL_REPORTS_QUERY, variables: { businessArea } },
      ],
    });
    console.log(response);
    if (!response.errors && response.data.createReport) {
      showMessage('Report created.', {
        pathname: `/${businessArea}/reporting/${response.data.createReport.report.id}`,
        historyMethod: 'push',
      });
    } else {
      showMessage('Report create action failed.');
    }
  };
  return (
    <>
      <Button
        color='primary'
        variant='contained'
        onClick={() => setDialogOpen(true)}
      >
        NEW REPORT
      </Button>
      <Dialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        scroll='paper'
        PaperComponent={React.forwardRef((props, ref) => (
          <Paper
            {...{
              ...props,
              ref,
            }}
            data-cy='dialog-setup-new-report'
          />
        ))}
        aria-labelledby='form-dialog-title'
      >
        <Formik
          initialValues={initialValue}
          onSubmit={submitFormHandler}
          // validationSchema={validationSchema}
        >
          {({ submitForm, values }) => (
            <>
              <DialogTitleWrapper>
                <DialogTitle id='scroll-dialog-title' disableTypography>
                  <Typography variant='h6'>Generate New Report</Typography>
                </DialogTitle>
              </DialogTitleWrapper>
              <DialogContent>
                <Form>
                  <Grid container spacing={3}>
                    <Grid item xs={12}>
                      <Field
                        name='reportType'
                        label='Report Type'
                        fullWidth
                        variant='outlined'
                        required
                        choices={choicesData.reportTypesChoices}
                        component={FormikSelectField}
                      />
                    </Grid>
                    <Grid item xs={12}>
                      <Grid container spacing={3}>
                        <Grid item xs={6}>
                          <Field
                            name='dateFrom'
                            label='Start Date'
                            component={FormikDateField}
                            required
                            fullWidth
                            decoratorEnd={
                              <CalendarTodayRoundedIcon color='disabled' />
                            }
                          />
                        </Grid>
                        <Grid item xs={6}>
                          <Field
                            name='dateTo'
                            label='End Date'
                            component={FormikDateField}
                            required
                            disabled={!values.dateFrom}
                            initialFocusedDate={values.dateFrom}
                            fullWidth
                            decoratorEnd={
                              <CalendarTodayRoundedIcon color='disabled' />
                            }
                            minDate={values.dateFrom}
                          />
                        </Grid>
                      </Grid>
                    </Grid>
                    <Grid item xs={12}>
                      <Field
                        name='adminArea'
                        label='Administrative Level 2'
                        variant='outlined'
                        component={FormikAdminAreaAutocomplete}
                      />
                    </Grid>
                    {/* <Grid item xs={12}>
                      <Field
                        name='program'
                        label='Programme'
                        fullWidth
                        variant='outlined'
                        required
                        choices={mappedPrograms}
                        component={FormikSelectField}
                      />
                    </Grid> */}
                    <Grid item xs={12}>
                      <Field
                        name='country'
                        fullWidth
                        variant='outlined'
                        label='Country'
                        component={FormikSelectField}
                        choices={choicesData.countriesChoices}
                      />
                    </Grid>
                  </Grid>
                </Form>
              </DialogContent>
              <DialogFooter>
                <DialogActions>
                  <Button onClick={() => setDialogOpen(false)}>CANCEL</Button>
                  <Button
                    type='submit'
                    color='primary'
                    variant='contained'
                    onClick={submitForm}
                    data-cy='button-submit'
                  >
                    GENERATE
                  </Button>
                </DialogActions>
              </DialogFooter>
            </>
          )}
        </Formik>
      </Dialog>
    </>
  );
};
