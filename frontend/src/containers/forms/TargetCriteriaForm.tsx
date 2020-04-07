import React from 'react';
import * as Yup from 'yup';
import styled from 'styled-components';
import {
  Dialog,
  DialogContent,
  DialogTitle,
  Typography,
  Button,
  DialogActions,
} from '@material-ui/core';
import { Field, Formik, FieldArray } from 'formik';
import { useImportedIndividualFieldsQuery } from '../../__generated__/graphql';
import { FormikSelectField } from '../../shared/Formik/FormikSelectField';
import { AddCircleOutline } from '@material-ui/icons';
import { FormikTextField } from '../../shared/Formik/FormikTextField';

const DialogTitleWrapper = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
`;

const DialogDescription = styled.div`
  margin: 20px 0;
  font-size: 14px;
  color: rgba(0, 0, 0, 0.54);
`;

const DialogContainer = styled.div`
  position: absolute;
`;

const DialogFooter = styled.div`
  padding: 12px 16px;
  margin: 0;
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  text-align: right;
`;

const AddCriteriaWrapper = styled.div`
  text-align: right;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: ${({ theme }) => theme.spacing(3)}px 0;
`;

const AddCriteria = styled.div`
  display: flex;
  align-items: center;
  color: #003c8f;
  text-transform: uppercase;
  cursor: pointer;
  svg {
    margin-right: ${({ theme }) => theme.spacing(2)}px;
  }
`;

const Divider = styled.div`
  border-top: 1px solid #b1b1b5;
  margin: ${({ theme }) => theme.spacing(10)}px 0;
  position: relative;
`;

const DividerLabel = styled.div`
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 500;
  color: #253b46;
  text-transform: uppercase;
  padding: 5px;
  border: 1px solid #b1b1b5;
  border-radius: 50%;
  background-color: #fff;
`;

const validationSchema = Yup.object().shape({
  filters: Yup.array().of(
    Yup.object().shape({
      fieldName: Yup.string().required('Label is required'),
    }),
  ),
});

interface ProgramFormPropTypes {
  criteria?;
  onSubmit: (values) => Promise<void>;
  renderSubmit: (submit: () => Promise<void>) => void;
  open: boolean;
  onClose: () => void;
  title: string;
}

export function TargetCriteriaForm({
  criteria,
  //onSubmit,
  addCriteria,
  open,
  onClose,
  title,
}): React.ReactElement {
  const { data, loading } = useImportedIndividualFieldsQuery();
  const initialValue = {
    filters: criteria.filters || [{ fieldName: '' }],
  };

  const chooseFieldType = (e, arrayHelpers, index) => {
    const subField = data.allFieldsAttributes.find(
      (attributes) => attributes.name === e.target.value,
    );
    const values = {
      isFlexField: subField.isFlexField,
      value: null,
      choices: null,
    };
    switch (subField.type) {
      case 'INTEGER':
        values.value = { from: '', to: '' };
        break;
      case 'SELECT_ONE':
        values.choices = subField.choices;
        break;
      default:
        values.value = null;
        break;
    }
    arrayHelpers.replace(index, {
      ...values,
      fieldName: e.target.value,
      type: subField.type,
    });
  };

  if (loading) return null;

  const subField = (field, index) => {
    switch (field.type) {
      case 'INTEGER':
        return (
          <>
            <Field
              name={`filters[${index}].value.from`}
              label={`${field.fieldName} from`}
              type='number'
              variant='filled'
              component={FormikTextField}
            />
            <Field
              name={`filters[${index}].value.to`}
              label={`${field.fieldName} to`}
              type='number'
              variant='filled'
              component={FormikTextField}
            />
          </>
        );
      case 'SELECT_ONE':
        return (
          <Field
            name={`filters[${index}].value`}
            label={`${field.fieldName}`}
            choices={field.choices}
            index={index}
            component={FormikSelectField}
          />
        );
      default:
        return <p>Dupa</p>;
    }
  };
  return (
    <DialogContainer>
      <Formik
        initialValues={initialValue}
        onSubmit={(values, bag) => {
          const dataToSend = values.filters.map((each) => ({
            ...each,
            arguments: [each.value],
          }));
          addCriteria({ filters: dataToSend });
          return bag.resetForm();
        }}
        validationSchema={validationSchema}
        enableReinitialize
      >
        {({ submitForm, values }) => (
          <>
            <Dialog
              open={open}
              onClose={onClose}
              scroll='paper'
              aria-labelledby='form-dialog-title'
            >
              <DialogTitleWrapper>
                <DialogTitle id='scroll-dialog-title' disableTypography>
                  <Typography variant='h6'>{title}</Typography>
                </DialogTitle>
              </DialogTitleWrapper>
              <DialogContent>
                <DialogDescription>
                  Lorem ipsum dolor sit amet consectetur adipisicing elit. Natus
                  tempora iusto maxime? Odit expedita ipsam natus eos?
                </DialogDescription>
                <FieldArray
                  name='filters'
                  render={(arrayHelpers) => (
                    <>
                      {values.filters.map((each, index) => {
                        return (
                          //eslint-disable-next-line
                          <div key={index}>
                            <Field
                              name={`filters[${index}].fieldName`}
                              label='Choose field type'
                              fullWidth
                              required
                              choices={data.allFieldsAttributes}
                              index={index}
                              value={each.fieldName || null}
                              onChange={(e) =>
                                chooseFieldType(e, arrayHelpers, index)
                              }
                              component={FormikSelectField}
                            />
                            {each.fieldName && subField(each, index)}
                            {(values.filters.length === 1 && index === 0) ||
                            index === values.filters.length - 1 ? null : (
                              <Divider>
                                <DividerLabel>And</DividerLabel>
                              </Divider>
                            )}
                          </div>
                        );
                      })}
                      <AddCriteriaWrapper>
                        <AddCriteria
                          onClick={() => arrayHelpers.push({ fieldname: '' })}
                        >
                          <AddCircleOutline />
                          <span>Add Criteria</span>
                        </AddCriteria>
                      </AddCriteriaWrapper>
                    </>
                  )}
                />
              </DialogContent>
              <DialogFooter>
                <DialogActions>
                  <Button onClick={() => onClose()}>Cancel</Button>
                  <Button
                    onClick={() => submitForm()}
                    type='submit'
                    color='primary'
                    variant='contained'
                  >
                    Save
                  </Button>
                </DialogActions>
              </DialogFooter>
            </Dialog>
          </>
        )}
      </Formik>
    </DialogContainer>
  );
}
