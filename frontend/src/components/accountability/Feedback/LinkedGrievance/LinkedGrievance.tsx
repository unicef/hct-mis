import { Box, Grid, Typography } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { FeedbackQuery } from '../../../../__generated__/graphql';
import { BlackLink } from '../../../core/BlackLink';
import { ContainerColumnWithBorder } from '../../../core/ContainerColumnWithBorder';
import { LabelizedField } from '../../../core/LabelizedField';
import { OverviewContainer } from '../../../core/OverviewContainer';
import { Title } from '../../../core/Title';

interface LinkedGrievanceProps {
  feedback: FeedbackQuery['feedback'];
  baseUrl: string;
}

export const LinkedGrievance = ({
  feedback,
  baseUrl,
}: LinkedGrievanceProps): React.ReactElement => {
  const { t } = useTranslation();
  return (
    <Grid item xs={4}>
      {feedback.linkedGrievance ? (
        <Box p={3}>
          <ContainerColumnWithBorder>
            <Title>
              <Typography variant='h6'>{t('Linked Grievance')}</Typography>
            </Title>
            <OverviewContainer>
              <LabelizedField label={t('Ticket Id')}>
                <BlackLink
                  to={`/${baseUrl}/grievance-and-feedback/${feedback.linkedGrievance.id}`}
                >
                  {feedback.linkedGrievance.unicefId}
                </BlackLink>
              </LabelizedField>
            </OverviewContainer>
          </ContainerColumnWithBorder>
        </Box>
      ) : null}
    </Grid>
  );
};
