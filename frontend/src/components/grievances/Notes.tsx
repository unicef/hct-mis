import {
  Avatar,
  Box,
  Button,
  Grid,
  Paper,
  Typography,
} from '@material-ui/core';
import { Field, Form, Formik } from 'formik';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import * as Yup from 'yup';
import { FormikTextField } from '../../shared/Formik/FormikTextField';
import { renderUserName } from '../../utils/utils';
import {
  GrievanceTicketDocument,
  GrievanceTicketQuery,
  useCreateGrievanceTicketNoteMutation,
  useMeQuery,
} from '../../__generated__/graphql';
import { OverviewContainerColumn } from '../core/OverviewContainerColumn';
import { UniversalMoment } from '../core/UniversalMoment';

const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;
const Name = styled.span`
  font-size: 16px;
`;
const Date = styled.span`
  font-size: 12px;
  color: #848484;
`;
const DescMargin = styled.div`
  margin-bottom: 35px;
  overflow: auto;
`;
const StyledBox = styled(Paper)`
  display: flex;
  flex-direction: column;
  width: 100%;
  padding: 26px 22px;
`;

export function Notes({
  notes,
  canAddNote,
}: {
  notes: GrievanceTicketQuery['grievanceTicket']['ticketNotes'];
  canAddNote: boolean;
}): React.ReactElement {
  const { t } = useTranslation();
  const { data: meData, loading: meLoading } = useMeQuery({
    fetchPolicy: 'cache-and-network',
  });

  const { id } = useParams();
  const [mutate] = useCreateGrievanceTicketNoteMutation();

  if (meLoading) {
    return null;
  }

  const note = (
    name: string,
    date: string,
    description: string,
    noteId: string,
  ): React.ReactElement => (
    <Grid container key={noteId}>
      <Grid item xs={2}>
        <Avatar alt={`${name} picture`} src='/static/images/avatar/1.jpg' />
      </Grid>
      <Grid item xs={10}>
        <Grid item xs={12}>
          <Box display='flex' justifyContent='space-between'>
            <Name>{name}</Name>
            <Date>
              <UniversalMoment withTime>{date}</UniversalMoment>
            </Date>
          </Box>
        </Grid>
        <Grid item xs={12}>
          <DescMargin>
            <p>{description}</p>
          </DescMargin>
        </Grid>
      </Grid>
    </Grid>
  );

  const mappedNotes = notes?.edges?.map((el) =>
    note(
      renderUserName(el.node.createdBy),
      el.node.createdAt,
      el.node.description,
      el.node.id,
    ),
  );

  const initialValues: { [key: string]: string } = {
    newNote: '',
  };

  const validationSchema = Yup.object().shape({
    newNote: Yup.string().required(t('Note cannot be empty')),
  });

  return (
    <Formik
      initialValues={initialValues}
      onSubmit={(values, { resetForm }) => {
        mutate({
          variables: {
            noteInput: { ticket: id, description: values.newNote },
          },
          refetchQueries: () => [
            { query: GrievanceTicketDocument, variables: { id } },
          ],
        });
        resetForm({});
      }}
      validationSchema={validationSchema}
    >
      {({ submitForm }) => (
        <StyledBox>
          <Title>
            <Typography variant='h6'>Notes</Typography>
          </Title>
          <OverviewContainerColumn>
            {mappedNotes}
            {canAddNote && (
              <Grid container>
                <Grid item xs={2}>
                  <Avatar
                    src={`${meData.me.firstName || meData.me.email}`}
                    alt={`${meData.me.firstName || meData.me.email} picture`}
                  />
                </Grid>
                <Grid item xs={10}>
                  <Grid item xs={12}>
                    <Box display='flex' justifyContent='space-between'>
                      <Name>{renderUserName(meData.me)}</Name>
                    </Box>
                  </Grid>
                  <Grid item xs={12}>
                    <DescMargin>
                      <Form>
                        <Field
                          name='newNote'
                          multiline
                          fullWidth
                          variant='filled'
                          label='Add a note ...'
                          component={FormikTextField}
                        />
                        <Box mt={2} display='flex' justifyContent='flex-end'>
                          <Button
                            color='primary'
                            variant='contained'
                            onClick={submitForm}
                          >
                            {t('Add New Note')}
                          </Button>
                        </Box>
                      </Form>
                    </DescMargin>
                  </Grid>
                </Grid>
              </Grid>
            )}
          </OverviewContainerColumn>
        </StyledBox>
      )}
    </Formik>
  );
}
