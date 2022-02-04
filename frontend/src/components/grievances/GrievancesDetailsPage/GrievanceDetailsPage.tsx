import { Box, Grid, Typography } from '@material-ui/core';
import { isEmpty } from 'lodash';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { usePermissions } from '../../../hooks/usePermissions';
import {
  GRIEVANCE_CATEGORIES,
  GRIEVANCE_ISSUE_TYPES,
  GRIEVANCE_TICKET_STATES,
} from '../../../utils/constants';
import {
  decodeIdString,
  grievanceTicketStatusToColor,
  isPermissionDeniedError,
  reduceChoices,
  renderUserName,
} from '../../../utils/utils';
import {
  useGrievancesChoiceDataQuery,
  useGrievanceTicketQuery,
  useMeQuery,
} from '../../../__generated__/graphql';
import { ContainerColumnWithBorder } from '../../core/ContainerColumnWithBorder';
import { ContentLink } from '../../core/ContentLink';
import { LabelizedField } from '../../core/LabelizedField';
import { LoadingComponent } from '../../core/LoadingComponent';
import { OverviewContainer } from '../../core/OverviewContainer';
import { PermissionDenied } from '../../core/PermissionDenied';
import { StatusBox } from '../../core/StatusBox';
import { UniversalMoment } from '../../core/UniversalMoment';
import { AddIndividualGrievanceDetails } from '../AddIndividualGrievanceDetails';
import { DeleteIndividualGrievanceDetails } from '../DeleteIndividualGrievanceDetails';
import { FlagDetails } from '../FlagDetails';
import { GrievanceDetailsToolbar } from '../GrievanceDetailsToolbar';
import { NeedsAdjudicationDetails } from '../NeedsAdjudicationDetails';
import { Notes } from '../Notes';
import { OtherRelatedTickets } from '../OtherRelatedTickets';
import { PaymentIds } from '../PaymentIds';
import { ReassignRoleBox } from '../ReassignRoleBox';
import { RequestedHouseholdDataChange } from '../RequestedHouseholdDataChange';
import { RequestedIndividualDataChange } from '../RequestedIndividualDataChange';
import { grievancePermissions } from './grievancePermissions';

const PaddingContainer = styled.div`
  padding: 22px;
`;

const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

const StatusContainer = styled.div`
  min-width: 120px;
  max-width: 200px;
`;

export function GrievanceDetailsPage(): React.ReactElement {
  const { t } = useTranslation();
  const { id } = useParams();
  const permissions = usePermissions();
  const {
    data: currentUserData,
    loading: currentUserDataLoading,
  } = useMeQuery();
  const { data, loading, error } = useGrievanceTicketQuery({
    variables: { id },
    fetchPolicy: 'network-only',
  });
  const ticket = data?.grievanceTicket;
  const currentUserId = currentUserData?.me?.id;
  const isCreator = currentUserId === ticket?.createdBy?.id;
  const isOwner = currentUserId === ticket?.assignedTo?.id;

  const businessArea = useBusinessArea();
  const {
    data: choicesData,
    loading: choicesLoading,
  } = useGrievancesChoiceDataQuery();

  if (choicesLoading || loading || currentUserDataLoading)
    return <LoadingComponent />;
  if (isPermissionDeniedError(error)) return <PermissionDenied />;

  if (!data || !choicesData || !currentUserData || permissions === null)
    return null;

  const statusChoices: {
    [id: number]: string;
  } = reduceChoices(choicesData.grievanceTicketStatusChoices);

  const categoryChoices: {
    [id: number]: string;
  } = reduceChoices(choicesData.grievanceTicketCategoryChoices);

  const issueType = ticket.issueType
    ? choicesData.grievanceTicketIssueTypeChoices
        .filter((el) => el.category === ticket.category.toString())[0]
        .subCategories.filter(
          (el) => el.value === ticket.issueType.toString(),
        )[0].name
    : '-';

  const {
    canViewHouseholdDetails,
    canViewIndividualDetails,
    canEdit,
    canAddNote,
    canSetInProgress,
    canSetOnHold,
    canSendForApproval,
    canSendBack,
    canClose,
    canApproveDataChange,
    canApproveFlagAndAdjudication,
    canAssign,
  } = grievancePermissions(isCreator, isOwner, ticket, permissions);

  const FieldsArray: {
    label: string;
    value: React.ReactElement;
    size: boolean | 3 | 6 | 8 | 11 | 'auto' | 1 | 2 | 4 | 5 | 7 | 9 | 10 | 12;
  }[] = [
    {
      label: t('STATUS'),
      value: (
        <StatusContainer>
          <StatusBox
            status={statusChoices[ticket.status]}
            statusToColor={grievanceTicketStatusToColor}
          />
        </StatusContainer>
      ),
      size: 3,
    },
    {
      label: t('CATEGORY'),
      value: <span>{categoryChoices[ticket.category]}</span>,
      size: 3,
    },
    {
      label: t('Issue Type'),
      value: <span>{issueType}</span>,
      size: 6,
    },
    {
      label: t('HOUSEHOLD ID'),
      value: (
        <span>
          {ticket.household?.id ? (
            <ContentLink
              href={
                canViewHouseholdDetails
                  ? `/${businessArea}/population/household/${ticket.household.id}`
                  : undefined
              }
            >
              {ticket.household.unicefId}
            </ContentLink>
          ) : (
            '-'
          )}
        </span>
      ),
      size: 3,
    },
    {
      label: t('INDIVIDUAL ID'),
      value: (
        <span>
          {ticket.individual?.id ? (
            <ContentLink
              href={
                canViewIndividualDetails
                  ? `/${businessArea}/population/individuals/${ticket.individual.id}`
                  : undefined
              }
            >
              {ticket.individual.unicefId}
            </ContentLink>
          ) : (
            '-'
          )}
        </span>
      ),
      size: 3,
    },
    {
      label: t('PAYMENT ID'),
      value: (
        <span>
          {ticket.paymentRecord?.id ? (
            <ContentLink
              href={`/${businessArea}/payment-records/${ticket.paymentRecord.id}`}
            >
              {decodeIdString(ticket.paymentRecord.id)}
            </ContentLink>
          ) : (
            '-'
          )}
        </span>
      ),
      size: 6,
    },
    {
      label: t('CONSENT'),
      value: <span>{ticket.consent ? 'Yes' : 'No'}</span>,
      size: 3,
    },
    {
      label: t('CREATED BY'),
      value: <span>{renderUserName(ticket.createdBy)}</span>,
      size: 3,
    },
    {
      label: t('DATE CREATED'),
      value: <UniversalMoment>{ticket.createdAt}</UniversalMoment>,
      size: 3,
    },
    {
      label: t('LAST MODIFIED DATE'),
      value: <UniversalMoment>{ticket.updatedAt}</UniversalMoment>,
      size: 3,
    },
    {
      label: t('DESCRIPTION'),
      value: <span>{ticket.description || '-'}</span>,
      size: 6,
    },
    {
      label: t('ASSIGNED TO'),
      value: <span>{renderUserName(ticket.assignedTo) || '-'}</span>,
      size: 6,
    },
    {
      label: t('ADMINISTRATIVE LEVEL 2'),
      value: <span>{ticket.admin}</span>,
      size: 3,
    },
    {
      label: t('AREA / VILLAGE / PAY POINT'),
      value: <span>{ticket.area}</span>,
      size: 3,
    },
    {
      label: t('LANGUAGES SPOKEN'),
      value: <span>{ticket.language || '-'}</span>,
      size: 3,
    },
  ];
  const shouldShowReassignBoxDataChange = (): boolean => {
    let { individual } = ticket;
    let { household } = ticket;
    if (ticket.category.toString() === GRIEVANCE_CATEGORIES.DEDUPLICATION) {
      individual = ticket.needsAdjudicationTicketDetails.selectedIndividual;
      household =
        ticket.needsAdjudicationTicketDetails.selectedIndividual?.household;
    }
    const isOneIndividual = household.activeIndividualsCount === 1;

    if (isOneIndividual) return false;
    const isRightCategory =
      (ticket.category.toString() === GRIEVANCE_CATEGORIES.DATA_CHANGE &&
        ticket.issueType.toString() ===
          GRIEVANCE_ISSUE_TYPES.DELETE_INDIVIDUAL) ||
      (ticket.category.toString() === GRIEVANCE_CATEGORIES.DATA_CHANGE &&
        ticket.issueType.toString() ===
          GRIEVANCE_ISSUE_TYPES.EDIT_INDIVIDUAL) ||
      (ticket.category.toString() === GRIEVANCE_CATEGORIES.SYSTEM_FLAGGING &&
        ticket?.systemFlaggingTicketDetails?.approveStatus) ||
      (ticket.category.toString() === GRIEVANCE_CATEGORIES.DEDUPLICATION &&
        ticket?.needsAdjudicationTicketDetails?.selectedIndividual);

    if (!isRightCategory) return false;

    const isRightStatus =
      ticket.status === GRIEVANCE_TICKET_STATES.FOR_APPROVAL;
    if (!isRightStatus) return false;

    const householdsAndRoles = individual?.householdsAndRoles;
    const isHeadOfHousehold = individual?.id === household?.headOfHousehold?.id;
    const hasRolesToReassign =
      householdsAndRoles?.filter((el) => el.role !== 'NO_ROLE').length > 0;

    let isProperDataChange = true;
    if (
      ticket.category.toString() === GRIEVANCE_CATEGORIES.DATA_CHANGE &&
      ticket.issueType.toString() === GRIEVANCE_ISSUE_TYPES.EDIT_INDIVIDUAL
    ) {
      if (
        isEmpty(ticket.individualDataUpdateTicketDetails.individualData.role) &&
        isEmpty(
          ticket.individualDataUpdateTicketDetails.individualData.relationship,
        )
      ) {
        isProperDataChange = false;
      }
    }

    return (isHeadOfHousehold || hasRolesToReassign) && isProperDataChange;
  };

  // const shouldShowReassignBoxFlag = (): boolean => {
  //   //add condition here
  //   return true;
  // };

  const renderRightSection = (): React.ReactElement => {
    if (
      ticket.category.toString() === GRIEVANCE_CATEGORIES.PAYMENT_VERIFICATION
    )
      return (
        <Box display='flex' flexDirection='column'>
          <Box mt={6}>
            <PaymentIds
              verifications={
                ticket.paymentVerificationTicketDetails?.paymentVerifications
                  ?.edges
              }
            />
          </Box>
          <Box mt={6}>
            <OtherRelatedTickets
              ticket={ticket}
              linkedTickets={ticket.relatedTickets}
            />
          </Box>
        </Box>
      );
    if (shouldShowReassignBoxDataChange()) {
      return (
        <PaddingContainer>
          <Box display='flex' flexDirection='column'>
            <ReassignRoleBox
              shouldDisplayButton
              shouldDisableButton={
                ticket.deleteIndividualTicketDetails?.approveStatus
              }
              ticket={ticket}
            />
          </Box>
        </PaddingContainer>
      );
    }
    // if (shouldShowReassignBoxFlag())
    //   return (
    //     <PaddingContainer>
    //       <Box display='flex' flexDirection='column'>
    //         <ReassignRoleBox shouldDisplayButton={false} ticket={ticket} />
    //       </Box>
    //     </PaddingContainer>
    //   );
    return (
      <PaddingContainer>
        <Box display='flex' flexDirection='column'>
          <OtherRelatedTickets
            ticket={ticket}
            linkedTickets={ticket.relatedTickets}
          />
        </Box>
      </PaddingContainer>
    );
  };

  return (
    <div>
      <GrievanceDetailsToolbar
        ticket={ticket}
        canEdit={canEdit}
        canSetInProgress={canSetInProgress}
        canSetOnHold={canSetOnHold}
        canSendForApproval={canSendForApproval}
        canSendBack={canSendBack}
        canClose={canClose}
        canAssign={canAssign}
      />
      <Grid container>
        <Grid item xs={12}>
          <ContainerColumnWithBorder>
            <Title>
              <Typography variant='h6'>{t('Details')}</Typography>
            </Title>
            <OverviewContainer>
              <Grid container spacing={6}>
                {FieldsArray.map((el) => (
                  <Grid key={el.label} item xs={el.size}>
                    <LabelizedField label={el.label}>{el.value}</LabelizedField>
                  </Grid>
                ))}
              </Grid>
            </OverviewContainer>
          </ContainerColumnWithBorder>
        </Grid>
        <Grid item xs={12}>
          {ticket?.category?.toString() ===
            GRIEVANCE_CATEGORIES.SYSTEM_FLAGGING && (
            <PaddingContainer>
              <FlagDetails
                ticket={ticket}
                canApproveFlag={canApproveFlagAndAdjudication}
              />
            </PaddingContainer>
          )}
          {ticket?.category?.toString() ===
            GRIEVANCE_CATEGORIES.DEDUPLICATION && (
            <PaddingContainer>
              <NeedsAdjudicationDetails
                ticket={ticket}
                canApprove={canApproveFlagAndAdjudication}
              />
            </PaddingContainer>
          )}
          {ticket?.issueType?.toString() ===
            GRIEVANCE_ISSUE_TYPES.ADD_INDIVIDUAL && (
            <PaddingContainer>
              <AddIndividualGrievanceDetails
                ticket={ticket}
                canApproveDataChange={canApproveDataChange}
              />
            </PaddingContainer>
          )}
          {ticket?.issueType?.toString() ===
            GRIEVANCE_ISSUE_TYPES.DELETE_INDIVIDUAL && (
            <PaddingContainer>
              <DeleteIndividualGrievanceDetails
                ticket={ticket}
                canApproveDataChange={canApproveDataChange}
              />
            </PaddingContainer>
          )}
          {ticket?.issueType?.toString() ===
            GRIEVANCE_ISSUE_TYPES.EDIT_INDIVIDUAL && (
            <PaddingContainer>
              <RequestedIndividualDataChange
                ticket={ticket}
                canApproveDataChange={canApproveDataChange}
              />
            </PaddingContainer>
          )}
          {ticket?.issueType?.toString() ===
            GRIEVANCE_ISSUE_TYPES.EDIT_HOUSEHOLD && (
            <PaddingContainer>
              <RequestedHouseholdDataChange
                ticket={ticket}
                canApproveDataChange={canApproveDataChange}
              />
            </PaddingContainer>
          )}
        </Grid>
        <Grid item xs={9}>
          <PaddingContainer>
            <Notes notes={ticket.ticketNotes} canAddNote={canAddNote} />
          </PaddingContainer>
        </Grid>
        <Grid item xs={3}>
          {renderRightSection()}
        </Grid>
      </Grid>
    </div>
  );
}
