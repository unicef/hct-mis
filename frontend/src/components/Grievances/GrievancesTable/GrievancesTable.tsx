import React from 'react';
import styled from 'styled-components';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { UniversalTable } from '../../../containers/tables/UniversalTable';
import { usePermissions } from '../../../hooks/usePermissions';
import { GRIEVANCE_CATEGORIES } from '../../../utils/constants';
import { decodeIdString, reduceChoices } from '../../../utils/utils';
import {
  AllGrievanceTicketQuery,
  AllGrievanceTicketQueryVariables,
  GrievanceTicketNode,
  useAllGrievanceTicketQuery,
  useGrievancesChoiceDataQuery,
  useMeQuery,
} from '../../../__generated__/graphql';
import { LoadingComponent } from '../../LoadingComponent';
import { headCells } from './GrievancesTableHeadCells';
import { GrievancesTableRow } from './GrievancesTableRow';

const TableWrapper = styled.div`
  padding: 20px;
`;

interface GrievancesTableProps {
  businessArea: string;
  filter;
}

export const GrievancesTable = ({
  businessArea,
  filter,
}: GrievancesTableProps): React.ReactElement => {
  const initialVariables: AllGrievanceTicketQueryVariables = {
    businessArea,
    search: filter.search,
    status: [filter.status],
    fsp: [filter.fsp],
    createdAtRange: JSON.stringify(filter.createdAtRange),
    admin: [decodeIdString(filter?.admin?.node?.id)],
  };

  const {
    data: choicesData,
    loading: choicesLoading,
  } = useGrievancesChoiceDataQuery();
  const {
    data: currentUserData,
    loading: currentUserDataLoading,
  } = useMeQuery();
  const permissions = usePermissions();
  if (choicesLoading || currentUserDataLoading) return <LoadingComponent />;
  if (!choicesData || !currentUserData || permissions === null) return null;

  const statusChoices: {
    [id: number]: string;
  } = reduceChoices(choicesData.grievanceTicketStatusChoices);

  const categoryChoices: {
    [id: number]: string;
  } = reduceChoices(choicesData.grievanceTicketCategoryChoices);

  const currentUserId = currentUserData.me.id;

  const getCanViewDetailsOfTicket = (
    ticket: AllGrievanceTicketQuery['allGrievanceTicket']['edges'][number]['node'],
  ) => {
    const isTicketCreator = currentUserId === ticket.createdBy?.id;
    const isTicketOwner = currentUserId === ticket.assignedTo?.id;
    if (
      ticket.category.toString() === GRIEVANCE_CATEGORIES.SENSITIVE_GRIEVANCE
    ) {
      return (
        hasPermissions(
          PERMISSIONS.GRIEVANCES_VIEW_DETAILS_SENSITIVE,
          permissions,
        ) ||
        (isTicketCreator &&
          hasPermissions(
            PERMISSIONS.GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_CREATOR,
            permissions,
          )) ||
        (isTicketOwner &&
          hasPermissions(
            PERMISSIONS.GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_OWNER,
            permissions,
          ))
      );
    }
    return (
      hasPermissions(
        PERMISSIONS.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE,
        permissions,
      ) ||
      (isTicketCreator &&
        hasPermissions(
          PERMISSIONS.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_CREATOR,
          permissions,
        )) ||
      (isTicketOwner &&
        hasPermissions(
          PERMISSIONS.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_OWNER,
          permissions,
        ))
    );
  };

  return (
    <TableWrapper>
      <UniversalTable<
        AllGrievanceTicketQuery['allGrievanceTicket']['edges'][number]['node'],
        AllGrievanceTicketQueryVariables
      >
        headCells={headCells}
        title='Grievance and Feedback List'
        rowsPerPageOptions={[10, 15, 20]}
        query={useAllGrievanceTicketQuery}
        queriedObjectName='allGrievanceTicket'
        initialVariables={initialVariables}
        renderRow={(row) => (
          <GrievancesTableRow
            key={row.id}
            ticket={row}
            statusChoices={statusChoices}
            categoryChoices={categoryChoices}
            canViewDetails={getCanViewDetailsOfTicket(row)}
          />
        )}
      />
    </TableWrapper>
  );
};
