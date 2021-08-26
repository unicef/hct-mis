import React, { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import {
  AllUsersQueryVariables,
  useAllUsersQuery,
  UserNode,
} from '../../../__generated__/graphql';
import { UniversalTable } from '../UniversalTable';
import { headCells } from './UsersListTableHeadCells';
import { UsersListTableRow } from './UsersListTableRow';

const TableWrapper = styled.div`
  padding: 20px;
`;

interface UsersListTableProps {
  filter;
}

export const UsersListTable = ({
  filter,
}: UsersListTableProps): ReactElement => {
  const { t } = useTranslation();
  const businessArea = useBusinessArea();

  const initialVariables = {
    search: filter.search,
    partner: filter.partner,
    roles: filter.roles,
    status: filter.status,
    businessArea,
  };
  return (
    <TableWrapper>
      <UniversalTable<UserNode, AllUsersQueryVariables>
        title={t('Users List')}
        headCells={headCells}
        rowsPerPageOptions={[10, 15, 20]}
        query={useAllUsersQuery}
        queriedObjectName='allUsers'
        defaultOrderBy='status'
        defaultOrderDirection='desc'
        initialVariables={initialVariables}
        renderRow={(row) => <UsersListTableRow user={row} key={row.id} />}
      />
    </TableWrapper>
  );
};
