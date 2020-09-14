import React from 'react';
import styled from 'styled-components';
import Moment from 'react-moment';
import TableCell from '@material-ui/core/TableCell';
import { UserNode } from '../../../__generated__/graphql';

import { TableRow } from '@material-ui/core';
import { Missing } from '../../../components/Missing';

const StatusContainer = styled.div`
  min-width: 120px;
  max-width: 200px;
`;

interface UsersListTableRowProps {
  user: UserNode;
}

export function UsersListTableRow({ user }: UsersListTableRowProps) {
  return (
    <TableRow key={user.id}>
      <TableCell align='left'>{`${user.firstName} ${user.lastName}`}</TableCell>
      <TableCell align='left'>
        <Missing />
      </TableCell>
      <TableCell align='left'>
        <Missing />
      </TableCell>
      <TableCell align='left'>{user.email}</TableCell>
      <TableCell align='left'>
        <Moment format='D MMM YYYY'>{user.lastLogin}</Moment>
      </TableCell>
    </TableRow>
  );
}
