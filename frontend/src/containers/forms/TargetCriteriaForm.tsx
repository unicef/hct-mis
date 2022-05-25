import React, { useEffect, useRef, useState } from 'react';
import * as Yup from 'yup';
import styled from 'styled-components';
import {
  Box,
  Button,
  Dialog,
  DialogContent,
  DialogTitle,
  Typography,
} from '@material-ui/core';
import { AddCircleOutline } from '@material-ui/icons';
import { Field, FieldArray, Formik } from 'formik';
import { useImportedIndividualFieldsQuery } from '../../__generated__/graphql';
import { DialogActions } from '../dialogs/DialogActions';
import {
  chooseFieldType,
  clearField,
  formatCriteriaFilters,
  formatCriteriaIndividualsFiltersBlocks,
  mapCriteriaToInitialValues,
} from '../../utils/targetingUtils';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { TargetingCriteriaFilter } from './TargetCriteriaFilter';
import { TargetCriteriaFilterBlocks } from './TargetCriteriaFilterBlocks';
import { useTranslation } from 'react-i18next';
import { FormikTextField } from '../../shared/Formik/FormikTextField';

const DialogTitleWrapper = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
`;

const AndDividerLabel = styled.div`
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
const AndDivider = styled.div`
  border-top: 1px solid #b1b1b5;
  margin: ${({ theme }) => theme.spacing(10)}px 0;
  position: relative;
`;

const DialogDescription = styled.div`
  margin: 20px 0;
  font-size: 14px;
  color: rgba(0, 0, 0, 0.54);
`;
const AddIcon = styled(AddCircleOutline)`
  margin-right: 10px;
`;
const ButtonBox = styled.div`
  width: 300px;
`;
const DialogError = styled.div`
  margin: 20px 0;
  font-size: 14px;
  color: ${({ theme }) => theme.palette.error.dark};
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

const StyledBox = styled(Box)`
  width: 100%;
`;

const validationSchema = Yup.object().shape({
  filters: Yup.array().of(
    Yup.object().shape({
      fieldName: Yup.string().required('Field Type is required'),
    }),
  ),
  individualsFiltersBlocks: Yup.array().of(
    Yup.object().shape({
      individualBlockFilters: Yup.array().of(
        Yup.object().shape({
          fieldName: Yup.string().required('Field Type is required'),
        }),
      ),
    }),
  ),
});
interface ArrayFieldWrapperProps {
  arrayHelpers;
}
class ArrayFieldWrapper extends React.Component<ArrayFieldWrapperProps> {
  getArrayHelpers(): object {
    const { arrayHelpers } = this.props;
    return arrayHelpers;
  }

  render(): React.ReactNode {
    const { children } = this.props;
    return children;
  }
}

interface TargetCriteriaFormPropTypes {
  criteria?;
  addCriteria: (values) => void;
  open: boolean;
  onClose: () => void;
  title: string;
  shouldShowWarningForIndividualFilter?: boolean;
}

const associatedWith = (type) => (item) => item.associatedWith === type;
const isNot = (type) => (item) => item.type !== type;

export function TargetCriteriaForm({
  criteria,
  addCriteria,
  open,
  onClose,
  title,
  shouldShowWarningForIndividualFilter,
}: TargetCriteriaFormPropTypes): React.ReactElement {
  const { t } = useTranslation();
  const businessArea = useBusinessArea();
  const { data, loading } = useImportedIndividualFieldsQuery({
    variables: {
      businessAreaSlug: businessArea,
    },
  });
  const filtersArrayWrapperRef = useRef(null);
  const individualsFiltersBlocksWrapperRef = useRef(null);
  const initialValues = mapCriteriaToInitialValues(criteria);
  const [individualData, setIndividualData] = useState(null);
  const [householdData, setHouseholdData] = useState(null);
  useEffect(() => {
    if (loading) return;
    const filteredIndividualData = {
      allFieldsAttributes: data.allFieldsAttributes
        .filter(associatedWith('Individual'))
        .filter(isNot('IMAGE')),
    };
    setIndividualData(filteredIndividualData);

    const filteredHouseholdData = {
      allFieldsAttributes: data.allFieldsAttributes.filter(
        associatedWith('Household'),
      ),
    };
    setHouseholdData(filteredHouseholdData);
  }, [data, loading]);
  const validate = ({
    filters,
    individualsFiltersBlocks,
  }): { nonFieldErrors?: string[] } => {
    const filterNull = (filter): boolean => filter.value === null;

    const filterEmptyFromTo = (filter): boolean =>
      filter.value?.hasOwnProperty('from') &&
      filter.value?.hasOwnProperty('to') &&
      !filter.value.from &&
      !filter.value.to;

    const hasFiltersNullValues = Boolean(filters.filter(filterNull).length);

    const hasFiltersEmptyFromToValues = Boolean(
      filters.filter(filterEmptyFromTo).length,
    );

    const hasFiltersErrors =
      hasFiltersNullValues || hasFiltersEmptyFromToValues;

    const hasIndividualsFiltersBlocksErrors = individualsFiltersBlocks.some(
      (block) => {
        const hasNulls = block.individualBlockFilters.some(filterNull);
        const hasFromToError = block.individualBlockFilters.some(
          filterEmptyFromTo,
        );

        return hasNulls || hasFromToError;
      },
    );

    const errors: { nonFieldErrors?: string[] } = {};
    if (hasFiltersErrors || hasIndividualsFiltersBlocksErrors) {
      errors.nonFieldErrors = ['You need to fill out missing values.'];
    }
    if (filters.length + individualsFiltersBlocks.length === 0) {
      errors.nonFieldErrors = [
        'You need to add at least one household filter or an individual block filter.',
      ];
    } else if (
      individualsFiltersBlocks.filter(
        (block) => block.individualBlockFilters.length === 0,
      ).length > 0
    ) {
      errors.nonFieldErrors = [
        'You need to add at least one household filter or an individual block filter.',
      ];
    }
    return errors;
  };

  const handleSubmit = (values, bag): void => {
    const filters = formatCriteriaFilters(values.filters);
    const individualsFiltersBlocks = formatCriteriaIndividualsFiltersBlocks(
      values.individualsFiltersBlocks,
    );
    addCriteria({ filters, individualsFiltersBlocks });
    return bag.resetForm();
  };

  if (loading || !open) return null;

  return (
    <DialogContainer>
      <Formik
        initialValues={initialValues}
        onSubmit={handleSubmit}
        validate={validate}
        validationSchema={validationSchema}
        enableReinitialize
      >
        {({ submitForm, values, resetForm, errors }) => (
          <Dialog
            open={open}
            onClose={onClose}
            scroll='paper'
            aria-labelledby='form-dialog-title'
            fullWidth
            maxWidth='md'
          >
            <DialogTitleWrapper>
              <DialogTitle id='scroll-dialog-title' disableTypography>
                <Typography variant='h6'>{title}</Typography>
              </DialogTitle>
            </DialogTitleWrapper>
            <DialogContent>
              {// eslint-disable-next-line @typescript-eslint/ban-ts-ignore
              // @ts-ignore
              errors.nonFieldErrors && (
                <DialogError>
                  <ul>
                    {// eslint-disable-next-line @typescript-eslint/ban-ts-ignore
                    // @ts-ignore
                    errors.nonFieldErrors.map((message) => (
                      <li>{message}</li>
                    ))}
                  </ul>
                </DialogError>
              )}
              <DialogDescription>
                All rules defined below have to be true for the entire
                household.
              </DialogDescription>
              <FieldArray
                name='filters'
                render={(arrayHelpers) => (
                  <ArrayFieldWrapper
                    arrayHelpers={arrayHelpers}
                    ref={filtersArrayWrapperRef}
                  >
                    {values.filters.map((each, index) => {
                      return (
                        <TargetingCriteriaFilter
                          //eslint-disable-next-line
                          key={index}
                          index={index}
                          data={householdData}
                          each={each}
                          onChange={(e, object) => {
                            if (object) {
                              return chooseFieldType(
                                object,
                                arrayHelpers,
                                index,
                              );
                            }
                            return clearField(arrayHelpers, index);
                          }}
                          values={values}
                          onClick={() => arrayHelpers.remove(index)}
                        />
                      );
                    })}
                  </ArrayFieldWrapper>
                )}
              />
              <Box display='flex' flexDirection='column'>
                <ButtonBox>
                  <Button
                    onClick={() =>
                      filtersArrayWrapperRef.current
                        .getArrayHelpers()
                        .push({ fieldName: '' })
                    }
                    color='primary'
                  >
                    <AddIcon />
                    ADD HOUSEHOLD RULE
                  </Button>
                </ButtonBox>
              </Box>
              <AndDivider>
                <AndDividerLabel>And</AndDividerLabel>
              </AndDivider>
              {values.individualsFiltersBlocks.length &&
              shouldShowWarningForIndividualFilter ? (
                <DialogDescription>
                  In your programme, individual rules can only be applied to
                  head of households.
                </DialogDescription>
              ) : null}
              <FieldArray
                name='individualsFiltersBlocks'
                render={(arrayHelpers) => (
                  <ArrayFieldWrapper
                    arrayHelpers={arrayHelpers}
                    ref={individualsFiltersBlocksWrapperRef}
                  >
                    {values.individualsFiltersBlocks.map((each, index) => {
                      return (
                        <TargetCriteriaFilterBlocks
                          //eslint-disable-next-line
                          key={index}
                          blockIndex={index}
                          data={individualData}
                          values={values}
                          onDelete={() => arrayHelpers.remove(index)}
                        />
                      );
                    })}
                  </ArrayFieldWrapper>
                )}
              />
              <Box display='flex' flexDirection='column'>
                <ButtonBox>
                  <Button
                    onClick={() =>
                      individualsFiltersBlocksWrapperRef.current
                        .getArrayHelpers()
                        .push({
                          individualBlockFilters: [{ fieldName: '' }],
                        })
                    }
                    color='primary'
                  >
                    <AddIcon />
                    ADD INDIVIDUAL RULE GROUP
                  </Button>
                </ButtonBox>
              </Box>
              <Box mt={3}>
                <Typography>
                  {t(
                    'How many individuals in the household should fit these criteria?',
                  )}
                </Typography>
                <Box mt={2} display='flex'>
                  <Box mr={2}>
                    <Field
                      name='criteriaFitRangeMin'
                      type='number'
                      label={t('Min')}
                      color='primary'
                      component={FormikTextField}
                      variant='outlined'
                    />
                  </Box>
                  <Field
                    name='criteriaFitRangeMax'
                    type='number'
                    label={t('Max')}
                    color='primary'
                    component={FormikTextField}
                    variant='outlined'
                  />
                </Box>
              </Box>
            </DialogContent>
            <DialogFooter>
              <DialogActions>
                <StyledBox display='flex' justifyContent='flex-end'>
                  <div>
                    <Button
                      onClick={() => {
                        resetForm();
                        onClose();
                      }}
                    >
                      Cancel
                    </Button>
                    <Button
                      onClick={submitForm}
                      type='submit'
                      color='primary'
                      variant='contained'
                      data-cy='button-target-population-add-criteria'
                    >
                      Save
                    </Button>
                  </div>
                </StyledBox>
              </DialogActions>
            </DialogFooter>
          </Dialog>
        )}
      </Formik>
    </DialogContainer>
  );
}
