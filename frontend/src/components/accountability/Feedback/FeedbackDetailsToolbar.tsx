import { Box, Button } from '@material-ui/core';
import EditIcon from '@material-ui/icons/EditRounded';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useHistory, useParams } from 'react-router-dom';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { FeedbackQuery } from '../../../__generated__/graphql';
import { BreadCrumbsItem } from '../../core/BreadCrumbs';
import { PageHeader } from '../../core/PageHeader';

interface FeedbackDetailsToolbarProps {
  feedback: FeedbackQuery['feedback'];
  canEdit: boolean;
}

export const FeedbackDetailsToolbar = ({
  feedback,
  canEdit,
}: FeedbackDetailsToolbarProps): React.ReactElement => {
  const { t } = useTranslation();
  const { id } = useParams();
  const businessArea = useBusinessArea();
  const history = useHistory();

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Feedback'),
      to: `/${businessArea}/grievance/feedback`,
    },
  ];

  const hasLinkedGrievance = Boolean(feedback.linkedGrievance?.id);
  const isFeedbackWithHouseholdOnly = Boolean(
    feedback.householdLookup?.id && !feedback.individualLookup?.id,
  );

  return (
    <PageHeader
      title={`Feedback ID: ${feedback.unicefId}`}
      breadCrumbs={breadCrumbsItems}
    >
      <Box display='flex' alignItems='center'>
        {canEdit && (
          <Box mr={3}>
            <Button
              color='primary'
              variant='outlined'
              component={Link}
              to={`/${businessArea}/grievance/feedback/edit-ticket/${id}`}
              startIcon={<EditIcon />}
              data-cy='button-edit'
            >
              {t('Edit')}
            </Button>
          </Box>
        )}
        {!hasLinkedGrievance && (
          <Box mr={3}>
            <Button
              onClick={() =>
                history.push({
                  pathname: `/${businessArea}/grievance/new-ticket`,
                  state: {
                    selectedHousehold: feedback?.householdLookup,
                    selectedIndividual: feedback?.individualLookup,
                    linkedFeedbackId: id,
                    isFeedbackWithHouseholdOnly,
                  },
                })
              }
              variant='contained'
              color='primary'
            >
              {t('Create Linked Ticket')}
            </Button>
          </Box>
        )}
      </Box>
    </PageHeader>
  );
};
