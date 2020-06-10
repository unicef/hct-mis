import styled from 'styled-components';
import TableCell from '@material-ui/core/TableCell';
import React from 'react';
import { useHistory } from 'react-router-dom';
import moment from 'moment';
import { RegistrationDataImportNode } from '../../../../__generated__/graphql';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { ClickableTableRow } from '../../../../components/table/ClickableTableRow';
import { StatusBox } from '../../../../components/StatusBox';
import { registrationDataImportStatusToColor } from '../../../../utils/utils';

const StatusContainer = styled.div`
  width: 120px;
`;

interface PaymentRecordTableRowProps {
  registrationDataImport: RegistrationDataImportNode;
}

export function RegistrationDataImportTableRow({
  registrationDataImport,
}: PaymentRecordTableRowProps): React.ReactElement {
  const history = useHistory();
  const businessArea = useBusinessArea();
  const name = registrationDataImport.importedBy.firstName
    ? `${registrationDataImport.importedBy.firstName} ${registrationDataImport.importedBy.lastName}`
    : registrationDataImport.importedBy.email;
  const handleClick = (): void => {
    const path = `/${businessArea}/registration-data-import/${registrationDataImport.id}`;
    history.push(path);
  };
  return (
    <ClickableTableRow
      hover
      onClick={handleClick}
      role='checkbox'
      key={registrationDataImport.id}
    >
      <TableCell align='left'>{registrationDataImport.name}</TableCell>
      <TableCell align='left'>
        <StatusContainer>
          <StatusBox
            status={registrationDataImport.status}
            statusToColor={registrationDataImportStatusToColor}
          />
        </StatusContainer>
      </TableCell>
      <TableCell align='left'>
        {moment(registrationDataImport.importDate).format('DD MMM YYYY')}
      </TableCell>
      <TableCell align='right'>
        {registrationDataImport.numberOfHouseholds}
      </TableCell>
      <TableCell align='left'>{name}</TableCell>
      <TableCell align='left'>{registrationDataImport.dataSource}</TableCell>
    </ClickableTableRow>
  );
}
