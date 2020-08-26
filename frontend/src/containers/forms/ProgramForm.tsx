import React, { ReactElement } from 'react';
import * as Yup from 'yup';
import styled from 'styled-components';
import {
  Dialog,
  DialogContent,
  DialogTitle,
  Typography,
  Paper,
} from '@material-ui/core';
import CalendarTodayRoundedIcon from '@material-ui/icons/CalendarTodayRounded';
import { Field, Form, Formik } from 'formik';
import moment from 'moment';
import { FormikTextField } from '../../shared/Formik/FormikTextField';
import { FormikSelectField } from '../../shared/Formik/FormikSelectField';
import {
  ProgramNode,
  useProgrammeChoiceDataQuery,
} from '../../__generated__/graphql';
import { FormikRadioGroup } from '../../shared/Formik/FormikRadioGroup';
import { FormikDateField } from '../../shared/Formik/FormikDateField';
import { selectFields } from '../../utils/utils';
import { DialogActions } from '../dialogs/DialogActions';
import { FormikCheckboxField } from '../../shared/Formik/FormikCheckboxField';

const DialogTitleWrapper = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
`;

const DialogDescription = styled.div`
  margin: 20px 0;
  font-size: 14px;
  color: rgba(0, 0, 0, 0.54);
`;

const DialogFooter = styled.div`
  padding: 12px 16px;
  margin: 0;
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  text-align: right;
`;

const MediumLabel = styled.div`
  width: 60%;
  margin: 12px 0;
`;

const DateFields = styled.div`
  display: flex;
  justify-content: space-between;
  margin: 12px 0;
`;

const DateField = styled.div`
  width: 48%;
`;

const DialogContainer = styled.div`
  position: absolute;
`;
const FullWidth = styled.div`
  width: 100%;
`;

const validationSchema = Yup.object().shape({
  name: Yup.string().required('Programme name is required'),
  scope: Yup.string().required('CashAssist Scope is required'),
  startDate: Yup.date().required(),
  endDate: Yup.date()
    .when(
      'startDate',
      (startDate, schema) =>
        startDate &&
        schema.min(
          startDate,
          `End date have to be grater than ${moment(startDate).format(
            'DD/MM/YYYY',
          )}`,
        ),
      '',
    )
    .required(),
  sector: Yup.string().required('Sector is required'),
  budget: Yup.number().min(0),
});

interface ProgramFormPropTypes {
  program?: ProgramNode;
  onSubmit: (values) => Promise<void>;
  renderSubmit: (submit: () => Promise<void>) => ReactElement;
  open: boolean;
  onClose: () => void;
  title: string;
}

export function ProgramForm({
  program = null,
  onSubmit,
  renderSubmit,
  open,
  onClose,
  title,
}: ProgramFormPropTypes): ReactElement {
  const { data } = useProgrammeChoiceDataQuery();
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  let initialValue: { [key: string]: any } = {
    name: '',
    scope: '',
    startDate: '',
    endDate: '',
    description: '',
    budget: '0.00',
    administrativeAreasOfImplementation: '',
    populationGoal: 0,
    frequencyOfPayments: 'REGULAR',
    sector: '',
    cashPlus: false,
    individualDataNeeded: false,
  };

  if (program) {
    initialValue = selectFields(program, Object.keys(initialValue));
  }
  if (initialValue.budget === 0) {
    initialValue.budget = '0.00';
  }
  // initialValue.budget =
  if (!data) return null;
  return (
    <DialogContainer>
      <Dialog
        open={open}
        onClose={onClose}
        scroll='paper'
        PaperComponent={React.forwardRef((props, ref) => (
          <Paper
            {...{
              ...props,
              ref,
            }}
            data-cy='dialog-setup-new-programme'
          />
        ))}
        aria-labelledby='form-dialog-title'
      >
        <Formik
          initialValues={initialValue}
          onSubmit={(values) => {
            const newValues = { ...values };
            newValues.budget = Number(values.budget).toFixed(2);
            return onSubmit(values);
          }}
          validationSchema={validationSchema}
        >
          {({ submitForm, values }) => (
            <>
              <DialogTitleWrapper>
                <DialogTitle id='scroll-dialog-title' disableTypography>
                  <Typography variant='h6'>{title}</Typography>
                </DialogTitle>
              </DialogTitleWrapper>
              <DialogContent>
                <DialogDescription>
                  To create a new Programme, please complete all required fields
                  on the form below and save.
                </DialogDescription>

                <Form>
                  <Field
                    name='name'
                    label='Programme Name'
                    type='text'
                    fullWidth
                    required
                    variant='filled'
                    component={FormikTextField}
                  />
                  <Field
                    name='scope'
                    label='CashAssist Scope'
                    fullWidth
                    variant='filled'
                    required
                    choices={data.programScopeChoices}
                    component={FormikSelectField}
                  />
                  <DateFields>
                    <DateField>
                      <Field
                        name='startDate'
                        label='Start Date'
                        component={FormikDateField}
                        required
                        fullWidth
                        decoratorEnd={
                          <CalendarTodayRoundedIcon color='disabled' />
                        }
                      />
                    </DateField>
                    <DateField>
                      <Field
                        name='endDate'
                        label='End Date'
                        component={FormikDateField}
                        required
                        disabled={!values.startDate}
                        initialFocusedDate={values.startDate}
                        fullWidth
                        decoratorEnd={
                          <CalendarTodayRoundedIcon color='disabled' />
                        }
                        minDate={values.startDate}
                      />
                    </DateField>
                  </DateFields>
                  <Field
                    name='description'
                    label='Description'
                    type='text'
                    fullWidth
                    multiline
                    variant='filled'
                    component={FormikTextField}
                  />
                  <Field
                    name='budget'
                    label='Budget'
                    type='number'
                    fullWidth
                    precision={2}
                    variant='filled'
                    component={FormikTextField}
                  />
                  <Field
                    name='frequencyOfPayments'
                    label='Frequency of Payment'
                    choices={data.programFrequencyOfPaymentsChoices}
                    component={FormikRadioGroup}
                  />
                  <Field
                    name='administrativeAreasOfImplementation'
                    label='Administrative Areas of Implementation'
                    type='text'
                    fullWidth
                    variant='filled'
                    component={FormikTextField}
                  />
                  <Field
                    name='populationGoal'
                    label='Population goal'
                    type='number'
                    fullWidth
                    variant='filled'
                    component={FormikTextField}
                  />
                  <Field
                    name='sector'
                    label='Sector'
                    fullWidth
                    required
                    variant='filled'
                    choices={data.programSectorChoices}
                    component={FormikSelectField}
                  />
                  <FullWidth>
                    <Field
                      name='cashPlus'
                      label='Cash+'
                      color='primary'
                      component={FormikCheckboxField}
                    />
                  </FullWidth>
                  <FullWidth>
                    <Field
                      name='individualDataNeeded'
                      label="Will this programme use individuals’ data for targeting or entitlement calculation? Setting this flag can reduce the number of households filtered in the target population."
                      disabled={program && program.status === 'ACTIVE'}
                      color='primary'
                      component={FormikCheckboxField}
                    />
                  </FullWidth>
                </Form>
                <DialogDescription>
                  This programme will use Individuals’ data for entitlement
                  calculation. Hope has the data on all Individuals within the
                  targeted households and will send this to CashAssist.
                </DialogDescription>
              </DialogContent>
              <DialogFooter>
                <DialogActions>{renderSubmit(submitForm)}</DialogActions>
              </DialogFooter>
            </>
          )}
        </Formik>
      </Dialog>
    </DialogContainer>
  );
}
