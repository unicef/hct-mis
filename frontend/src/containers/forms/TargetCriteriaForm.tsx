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
  IconButton,
} from '@material-ui/core';
import { Field, Formik, FieldArray } from 'formik';
import { useImportedIndividualFieldsQuery } from '../../__generated__/graphql';
import { FormikSelectField } from '../../shared/Formik/FormikSelectField';
import { AddCircleOutline, Delete, FilterSharp } from '@material-ui/icons';
import { FormikTextField } from '../../shared/Formik/FormikTextField';
import { SubField } from '../../components/TargetPopulation/SubField';
import {
  formatCriteriaFilters,
  mapCriteriasToInitialValues,
} from '../../utils/utils';

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

const FlexWrapper = styled.div`
  display: flex;
  justify-content: space-between;
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
  const mappedFilters = mapCriteriasToInitialValues(criteria);
  const initialValue = {
    filters: mappedFilters,
  };

  //create a hook?
  const chooseFieldType = (e, arrayHelpers, index) => {
    const subFieldData = data.allFieldsAttributes.find(
      (attributes) => attributes.name === e.target.value,
    );
    const values = {
      isFlexField: subFieldData.isFlexField,
      fieldAttribute: {
        labelEn: subFieldData.labelEn,
        type: subFieldData.type,
        choices: null,
      },
      value: null,
    };
    switch (subFieldData.type) {
      case 'INTEGER':
        values.value = { from: '', to: '' };
        break;
      case 'SELECT_ONE':
        values.fieldAttribute.choices = subFieldData.choices;
        break;
      case 'SELECT_MANY':
        values.value = [];
        values.fieldAttribute.choices = subFieldData.choices;
        break;
      default:
        values.value = null;
        break;
    }
    arrayHelpers.replace(index, {
      ...values,
      fieldName: e.target.value,
      type: subFieldData.type,
    });
  };

  if (loading) return null;

  return (
    <DialogContainer>
      <Formik
        initialValues={initialValue}
        onSubmit={(values, bag) => {
          const dataToSend = formatCriteriaFilters(values);
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
                            <FlexWrapper>
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
                              <IconButton>
                                <Delete
                                  onClick={() => arrayHelpers.remove(index)}
                                />
                              </IconButton>
                            </FlexWrapper>
                            {each.fieldName && SubField(each, index)}
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
