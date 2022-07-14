import { Box, Button, FormHelperText, Grid } from '@material-ui/core';
import { Field, Formik } from 'formik';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useParams } from 'react-router-dom';
import styled from 'styled-components';
import {
  hasCreatorOrOwnerPermissions,
  PERMISSIONS,
} from '../../../config/permissions';
import { useArrayToDict } from '../../../hooks/useArrayToDict';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { usePermissions } from '../../../hooks/usePermissions';
import { useSnackbar } from '../../../hooks/useSnackBar';
import { FormikAdminAreaAutocomplete } from '../../../shared/Formik/FormikAdminAreaAutocomplete';
import { FormikCheckboxField } from '../../../shared/Formik/FormikCheckboxField';
import { FormikSelectField } from '../../../shared/Formik/FormikSelectField';
import { FormikTextField } from '../../../shared/Formik/FormikTextField';
import {
  GRIEVANCE_CATEGORIES,
  GRIEVANCE_TICKET_STATES,
} from '../../../utils/constants';
import {
  isInvalid,
  isPermissionDeniedError,
  renderUserName,
  thingForSpecificGrievanceType,
} from '../../../utils/utils';
import {
  GrievanceTicketDocument,
  useAllAddIndividualFieldsQuery,
  useAllEditHouseholdFieldsQuery,
  useAllUsersQuery,
  useGrievancesChoiceDataQuery,
  useGrievanceTicketQuery,
  useGrievanceTicketStatusChangeMutation,
  useMeQuery,
  useUpdateGrievanceMutation,
} from '../../../__generated__/graphql';
import { BreadCrumbsItem } from '../../../components/core/BreadCrumbs';
import { ContainerColumnWithBorder } from '../../../components/core/ContainerColumnWithBorder';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PageHeader } from '../../../components/core/PageHeader';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { Consent } from '../../../components/grievances/Consent';
import { LookUpSection } from '../../../components/grievances/LookUpSection';
import { OtherRelatedTicketsCreate } from '../../../components/grievances/OtherRelatedTicketsCreate';
import {
  dataChangeComponentDict,
  EmptyComponent,
  prepareInitialValues,
  prepareVariables,
} from '../../../components/grievances/utils/editGrievanceUtils';
import { validate } from '../../../components/grievances/utils/validateGrievance';
import { validationSchema } from '../../../components/grievances/utils/validationSchema';
import { LoadingButton } from '../../../components/core/LoadingButton';

const BoxPadding = styled.div`
  padding: 15px 0;
`;
const NewTicket = styled.div`
  padding: 20px;
`;
const BoxWithBorderBottom = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  padding: 15px 0;
`;
const BoxWithBorders = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  padding: 15px 0;
`;

export const EditGrievancePage = (): React.ReactElement => {
  const { t } = useTranslation();
  const businessArea = useBusinessArea();
  const permissions = usePermissions();
  const { showMessage } = useSnackbar();
  const { id } = useParams();

  const {
    data: ticketData,
    loading: ticketLoading,
    error,
  } = useGrievanceTicketQuery({
    variables: {
      id,
    },
    fetchPolicy: 'cache-and-network',
  });
  const {
    data: currentUserData,
    loading: currentUserDataLoading,
  } = useMeQuery();

  const { data: userData, loading: userDataLoading } = useAllUsersQuery({
    variables: { businessArea, first: 1000 },
  });

  const {
    data: choicesData,
    loading: choicesLoading,
  } = useGrievancesChoiceDataQuery();

  const [mutate, { loading }] = useUpdateGrievanceMutation();
  const [mutateStatus] = useGrievanceTicketStatusChangeMutation();
  const {
    data: allAddIndividualFieldsData,
    loading: allAddIndividualFieldsDataLoading,
  } = useAllAddIndividualFieldsQuery();
  const {
    data: householdFieldsData,
    loading: householdFieldsLoading,
  } = useAllEditHouseholdFieldsQuery();
  const individualFieldsDict = useArrayToDict(
    allAddIndividualFieldsData?.allAddIndividualsFieldsAttributes,
    'name',
    '*',
  );
  const householdFieldsDict = useArrayToDict(
    householdFieldsData?.allEditHouseholdFieldsAttributes,
    'name',
    '*',
  );
  if (
    userDataLoading ||
    choicesLoading ||
    ticketLoading ||
    allAddIndividualFieldsDataLoading ||
    householdFieldsLoading ||
    currentUserDataLoading
  )
    return <LoadingComponent />;
  if (isPermissionDeniedError(error)) return <PermissionDenied />;
  if (
    !choicesData ||
    !userData ||
    !ticketData ||
    !currentUserData ||
    permissions === null ||
    !householdFieldsData ||
    !householdFieldsDict ||
    !individualFieldsDict
  )
    return null;

  const currentUserId = currentUserData.me.id;
  const ticket = ticketData.grievanceTicket;

  const isCreator = ticket.createdBy?.id === currentUserId;
  const isOwner = ticket.assignedTo?.id === currentUserId;
  if (
    !hasCreatorOrOwnerPermissions(
      PERMISSIONS.GRIEVANCES_UPDATE,
      isCreator,
      PERMISSIONS.GRIEVANCES_UPDATE_AS_CREATOR,
      isOwner,
      PERMISSIONS.GRIEVANCES_UPDATE_AS_OWNER,
      permissions,
    )
  )
    return <PermissionDenied />;

  const changeState = (status): void => {
    mutateStatus({
      variables: {
        grievanceTicketId: ticket.id,
        status,
      },
    });
  };
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const initialValues: any = prepareInitialValues(ticket);

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Grievance and Feedback'),
      to: `/${businessArea}/grievance-and-feedback/${ticket.id}`,
    },
  ];

  const mappedIndividuals = userData.allUsers.edges.map((edge) => ({
    name: renderUserName(edge.node),
    value: edge.node.id,
  }));

  const mappedPriorities = Array.from(Array(10).keys()).map((i) => ({
    name: (i + 1).toString(),
    value: i + 1,
  }));

  const issueTypeDict = choicesData.grievanceTicketIssueTypeChoices.reduce(
    (prev, curr) => {
      // eslint-disable-next-line no-param-reassign
      prev[curr.category] = curr;
      return prev;
    },
    {},
  );
  const dataChangeErrors = (errors, touched): React.ReactElement[] =>
    [
      'householdDataUpdateFields',
      'individualDataUpdateFields',
      'individualDataUpdateFieldsDocuments',
      'individualDataUpdateFieldsIdentities',
      'individualDataUpdateDocumentsToEdit',
      'individualDataUpdateIdentitiesToEdit',
      'individualDataUpdateFieldsPaymentChannels',
      'individualDataUpdatePaymentChannelsToEdit',
    ].map(
      (fieldname) =>
        isInvalid(fieldname, errors, touched) && (
          <FormHelperText error>{errors[fieldname]}</FormHelperText>
        ),
    );

  return (
    <Formik
      initialValues={initialValues}
      onSubmit={async (values) => {
        try {
          const { variables } = prepareVariables(businessArea, values, ticket);
          await mutate({
            variables,
            refetchQueries: () => [
              {
                query: GrievanceTicketDocument,
                variables: { id: ticket.id },
              },
            ],
          });
          showMessage(t('Grievance Ticket edited.'), {
            pathname: `/${businessArea}/grievance-and-feedback/${ticket.id}`,
            historyMethod: 'push',
          });
        } catch (e) {
          e.graphQLErrors.map((x) => showMessage(x.message));
        }
        if (
          ticket.status === GRIEVANCE_TICKET_STATES.FOR_APPROVAL ||
          ticket.status === GRIEVANCE_TICKET_STATES.ON_HOLD
        ) {
          changeState(GRIEVANCE_TICKET_STATES.IN_PROGRESS);
        }
      }}
      validate={(values) =>
        validate(
          values,
          allAddIndividualFieldsData,
          individualFieldsDict,
          householdFieldsDict,
        )
      }
      validationSchema={validationSchema}
    >
      {({ submitForm, values, setFieldValue, errors, touched }) => {
        const DatachangeComponent = thingForSpecificGrievanceType(
          values,
          dataChangeComponentDict,
          EmptyComponent,
        );
        return (
          <>
            <PageHeader
              title={`${t('Edit Ticket')} #${ticket.unicefId}`}
              breadCrumbs={breadCrumbsItems}
            >
              <Box display='flex' alignContent='center'>
                <Box mr={3}>
                  <Button
                    component={Link}
                    to={`/${businessArea}/grievance-and-feedback/${ticket.id}`}
                  >
                    {t('Cancel')}
                  </Button>
                </Box>
                <LoadingButton
                  loading={loading}
                  color='primary'
                  variant='contained'
                  onClick={submitForm}
                >
                  {t('Save')}
                </LoadingButton>
              </Box>
            </PageHeader>
            <Grid container spacing={3}>
              <Grid item xs={9}>
                <NewTicket>
                  <ContainerColumnWithBorder>
                    <Grid container spacing={3}>
                      <Grid item xs={6}>
                        <Field
                          name='category'
                          label={t('Category*')}
                          disabled
                          onChange={(e) => {
                            setFieldValue('category', e.target.value);
                            setFieldValue('issueType', null);
                            setFieldValue('subCategory', null);
                          }}
                          variant='outlined'
                          choices={choicesData.grievanceTicketCategoryChoices}
                          component={FormikSelectField}
                        />
                      </Grid>
                      {values.category.toString() ===
                        GRIEVANCE_CATEGORIES.GRIEVANCE_COMPLAINT && (
                        <Grid item xs={6}>
                          <Field
                            name='subCategory'
                            label={t('Sub Category')}
                            disabled={Boolean(ticket.subCategory)}
                            onChange={(e) => {
                              setFieldValue('subCategory', e.target.value);
                            }}
                            variant='outlined'
                            choices={
                              choicesData.grievanceTicketSubCategoryChoices
                            }
                            component={FormikSelectField}
                          />
                        </Grid>
                      )}
                      {values.category.toString() ===
                        GRIEVANCE_CATEGORIES.SENSITIVE_GRIEVANCE ||
                      values.category.toString() ===
                        GRIEVANCE_CATEGORIES.DATA_CHANGE ? (
                        <Grid item xs={6}>
                          <Field
                            name='issueType'
                            disabled
                            label={t('Issue Type*')}
                            variant='outlined'
                            choices={
                              issueTypeDict[values.category.toString()]
                                .subCategories
                            }
                            component={FormikSelectField}
                          />
                        </Grid>
                      ) : null}
                    </Grid>
                    <BoxWithBorders>
                      <Box display='flex' flexDirection='column'>
                        <Consent />
                        <Field
                          name='consent'
                          label={t('Received Consent*')}
                          color='primary'
                          disabled
                          component={FormikCheckboxField}
                        />
                        <LookUpSection
                          values={values}
                          disabledHouseholdIndividual={
                            values.selectedIndividual ||
                            values.selectedHousehold
                          }
                          disabledPaymentRecords
                          onValueChange={setFieldValue}
                          errors={errors}
                          touched={touched}
                        />
                      </Box>
                    </BoxWithBorders>
                    <BoxWithBorderBottom>
                      <Grid container spacing={3}>
                        <Grid item xs={6}>
                          <Field
                            name='assignedTo'
                            label={t('Assigned to*')}
                            variant='outlined'
                            choices={mappedIndividuals}
                            component={FormikSelectField}
                          />
                        </Grid>
                      </Grid>
                    </BoxWithBorderBottom>
                    <BoxPadding>
                      <Grid container spacing={3}>
                        <Grid item xs={12}>
                          <Field
                            name='description'
                            multiline
                            fullWidth
                            disabled={Boolean(ticket.description)}
                            variant='outlined'
                            label='Description*'
                            component={FormikTextField}
                          />
                        </Grid>
                        <Grid item xs={6}>
                          <Field
                            name='admin'
                            label={t('Administrative Level 2')}
                            disabled={Boolean(ticket.admin)}
                            variant='outlined'
                            component={FormikAdminAreaAutocomplete}
                          />
                        </Grid>
                        <Grid item xs={6}>
                          <Field
                            name='area'
                            fullWidth
                            disabled={Boolean(ticket.area)}
                            variant='outlined'
                            label={t('Area / Village / Pay point')}
                            component={FormikTextField}
                          />
                        </Grid>
                        <Grid item xs={6}>
                          <Field
                            name='language'
                            multiline
                            fullWidth
                            disabled={Boolean(ticket.language)}
                            variant='outlined'
                            label={t('Languages Spoken')}
                            component={FormikTextField}
                          />
                        </Grid>
                        <Grid item xs={6}>
                          <Field
                            name='priority'
                            multiline
                            fullWidth
                            disabled={Boolean(ticket.priority)}
                            variant='outlined'
                            label={t('Priority')}
                            choices={mappedPriorities}
                            component={FormikSelectField}
                          />
                        </Grid>
                      </Grid>
                    </BoxPadding>
                    {hasCreatorOrOwnerPermissions(
                      PERMISSIONS.GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE,
                      isCreator,
                      PERMISSIONS.GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE_AS_CREATOR,
                      isOwner,
                      PERMISSIONS.GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE_AS_OWNER,
                      permissions,
                    ) && (
                      <BoxPadding>
                        <DatachangeComponent
                          values={values}
                          setFieldValue={setFieldValue}
                        />
                        {dataChangeErrors(errors, touched)}
                      </BoxPadding>
                    )}
                  </ContainerColumnWithBorder>
                </NewTicket>
              </Grid>
              <Grid item xs={3}>
                <NewTicket>
                  {values.category && values.selectedHousehold?.id ? (
                    <OtherRelatedTicketsCreate values={values} />
                  ) : null}
                </NewTicket>
              </Grid>
            </Grid>
          </>
        );
      }}
    </Formik>
  );
};
