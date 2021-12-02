import {
  Box,
  Checkbox,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from '@material-ui/core';
import CheckCircleIcon from '@material-ui/icons/CheckCircle';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { GRIEVANCE_TICKET_STATES } from '../../../utils/constants';
import { GrievanceTicketQuery } from '../../../__generated__/graphql';
import { PhotoModal } from '../../PhotoModal/PhotoModal';

const GreenIcon = styled.div`
  color: #28cb15;
`;
const GreyText = styled.div`
  color: #9e9e9e;
`;

const StyledTable = styled(Table)`
  min-width: 100px;
`;

const Title = styled.div`
  padding-top: ${({ theme }) => theme.spacing(4)}px;
  padding-bottom: ${({ theme }) => theme.spacing(2)}px;
`;

export interface DocumentsToEditTableProps {
  values;
  isEdit;
  ticket: GrievanceTicketQuery['grievanceTicket'];
  setFieldValue;
  documentTypeDict;
  countriesDict;
  index;
  document;
}

export const DocumentsToEditTable = ({
  values,
  isEdit,
  ticket,
  setFieldValue,
  documentTypeDict,
  countriesDict,
  index,
  document,
}: DocumentsToEditTableProps) => {
  const { t } = useTranslation();
  const renderNewOrNotUpdated = (prev, curr): React.ReactElement => {
    if (prev === curr) {
      return <GreyText>{t('Not updated')}</GreyText>;
    }
    return <span>{curr}</span>;
  };
  const { selectedDocumentsToEdit } = values;
  const renderCurrentPhoto = (doc): React.ReactElement => {
    if (doc.value?.photo === doc.previous_value?.photo) {
      return <GreyText>{t('Not updated')}</GreyText>;
    }
    if (!document.value?.photo) {
      return <span>-</span>;
    }
    return <PhotoModal src={document.value.photo} />;
  };
  const handleSelectDocumentToEdit = (documentIndex): void => {
    const newSelected = [...selectedDocumentsToEdit];
    const selectedIndex = newSelected.indexOf(documentIndex);
    if (selectedIndex !== -1) {
      newSelected.splice(selectedIndex, 1);
    } else {
      newSelected.push(documentIndex);
    }
    setFieldValue('selectedDocumentsToEdit', newSelected);
  };

  return (
    <div key={document.previous_value.number}>
      <Title>
        <Box display='flex' justifyContent='space-between'>
          <Typography variant='h6'>{t('Document to be edited')}</Typography>
        </Box>
      </Title>
      <StyledTable>
        <TableHead>
          <TableRow>
            <TableCell align='left'>
              {isEdit ? (
                <Checkbox
                  color='primary'
                  onChange={(): void => {
                    handleSelectDocumentToEdit(index);
                  }}
                  disabled={
                    ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL
                  }
                  checked={selectedDocumentsToEdit.includes(index)}
                  inputProps={{ 'aria-labelledby': 'selected' }}
                />
              ) : (
                selectedDocumentsToEdit.includes(index) && (
                  <GreenIcon>
                    <CheckCircleIcon />
                  </GreenIcon>
                )
              )}
            </TableCell>
            <TableCell align='left'>{t('Field')}</TableCell>
            <TableCell align='left'>{t('Current Value')}</TableCell>
            <TableCell align='left'>{t('New Value')}</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          <TableRow>
            <TableCell />
            <TableCell align='left'>{t('Country')}</TableCell>
            <TableCell align='left'>
              {countriesDict[document.previous_value.country]}
            </TableCell>
            <TableCell align='left'>
              {renderNewOrNotUpdated(
                countriesDict[document.previous_value.country],
                countriesDict[document.value?.country],
              )}
            </TableCell>
          </TableRow>
          <TableRow>
            <TableCell />
            <TableCell align='left'>{t('Document Type')}</TableCell>
            <TableCell align='left'>
              {documentTypeDict[document.previous_value.type]}
            </TableCell>
            <TableCell align='left'>
              {renderNewOrNotUpdated(
                documentTypeDict[document.previous_value.type],
                documentTypeDict[document.value.type],
              )}
            </TableCell>
          </TableRow>
          <TableRow>
            <TableCell />

            <TableCell align='left'>{t('Document Number')}</TableCell>
            <TableCell align='left'>{document.previous_value.number}</TableCell>
            <TableCell align='left'>
              {renderNewOrNotUpdated(
                documentTypeDict[document.previous_value.number],
                documentTypeDict[document.value.number],
              )}
            </TableCell>
          </TableRow>
          <TableRow>
            <TableCell />
            <TableCell align='left'>{t('Photo')}</TableCell>
            <TableCell align='left'>
              {document.previous_value?.photo ? (
                <PhotoModal src={document.previous_value.photo} />
              ) : (
                '-'
              )}
            </TableCell>
            <TableCell align='left'>{renderCurrentPhoto(document)}</TableCell>
          </TableRow>
        </TableBody>
      </StyledTable>
    </div>
  );
};
