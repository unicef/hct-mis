import { Grid, GridSize, Typography } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { renderUserName } from '../../../../utils/utils';
import {
  FeedbackIssueType,
  FeedbackQuery,
} from '../../../../__generated__/graphql';
import { BlackLink } from '../../../core/BlackLink';
import { ContainerColumnWithBorder } from '../../../core/ContainerColumnWithBorder';
import { LabelizedField } from '../../../core/LabelizedField';
import { OverviewContainer } from '../../../core/OverviewContainer';
import { Title } from '../../../core/Title';
import { UniversalMoment } from '../../../core/UniversalMoment';
import { useBaseUrl } from '../../../../hooks/useBaseUrl';

interface FeedbackDetailsProps {
  feedback: FeedbackQuery['feedback'];
  canViewHouseholdDetails: boolean;
  canViewIndividualDetails: boolean;
}

export const FeedbackDetails = ({
  feedback,
  canViewHouseholdDetails,
  canViewIndividualDetails,
}: FeedbackDetailsProps): React.ReactElement => {
  const { t } = useTranslation();
  const { baseUrl, isAllPrograms } = useBaseUrl();

  return (
    <Grid item xs={12}>
      <ContainerColumnWithBorder>
        <Title>
          <Typography variant='h6'>{t('Details')}</Typography>
        </Title>
        <OverviewContainer>
          <Grid container spacing={6}>
            {[
              {
                label: t('Category'),
                value: <span>{t('Feedback')}</span>,
                size: 3,
              },
              {
                label: t('Issue Type'),
                value: (
                  <span>
                    {feedback.issueType === FeedbackIssueType.PositiveFeedback
                      ? 'Positive Feedback'
                      : 'Negative Feedback'}
                  </span>
                ),
                size: 3,
              },
              {
                label: t('Household ID'),
                value: (
                  <span>
                    {feedback.householdLookup?.id && !isAllPrograms ? (
                      <BlackLink
                        to={
                          canViewHouseholdDetails
                            ? `/${baseUrl}/population/household/${feedback.householdLookup.id}`
                            : undefined
                        }
                      >
                        {feedback.householdLookup.unicefId}
                      </BlackLink>
                    ) : (
                      feedback.householdLookup.unicefId || '-'
                    )}
                  </span>
                ),
                size: 3,
              },
              {
                label: t('Individual ID'),
                value: (
                  <span>
                    {feedback.individualLookup?.id && !isAllPrograms ? (
                      <BlackLink
                        to={
                          canViewIndividualDetails
                            ? `/${baseUrl}/population/individuals/${feedback.individualLookup.id}`
                            : undefined
                        }
                      >
                        {feedback.individualLookup.unicefId}
                      </BlackLink>
                    ) : (
                      feedback.individualLookup.unicefId || '-'
                    )}
                  </span>
                ),
                size: 3,
              },
              {
                label: t('Programme'),
                value: (
                  <span>
                    {feedback.program?.id ? (
                      <BlackLink
                        to={`/${baseUrl}/details/${feedback.program.id}`}
                      >
                        {feedback.program.name}
                      </BlackLink>
                    ) : (
                      '-'
                    )}
                  </span>
                ),
                size: 3,
              },
              {
                label: t('Created By'),
                value: renderUserName(feedback.createdBy),
                size: 3,
              },
              {
                label: t('Date Created'),
                value: <UniversalMoment>{feedback.createdAt}</UniversalMoment>,
                size: 3,
              },
              {
                label: t('Last Modified Date'),
                value: <UniversalMoment>{feedback.updatedAt}</UniversalMoment>,
                size: 3,
              },
              {
                label: t('Administrative Level 2'),
                value: feedback.admin2?.name,
                size: 3,
              },
              {
                label: t('Area / Village / Pay point'),
                value: feedback.area,
                size: 3,
              },
              {
                label: t('Languages Spoken'),
                value: feedback.language,
                size: 3,
              },
              {
                label: t('Description'),
                value: feedback.description,
                size: 12,
              },
              {
                label: t('Comments'),
                value: feedback.comments,
                size: 12,
              },
            ]
              .filter((el) => el)
              .map((el) => (
                <Grid key={el.label} item xs={el.size as GridSize}>
                  <LabelizedField label={el.label}>{el.value}</LabelizedField>
                </Grid>
              ))}
          </Grid>
        </OverviewContainer>
      </ContainerColumnWithBorder>
    </Grid>
  );
};
