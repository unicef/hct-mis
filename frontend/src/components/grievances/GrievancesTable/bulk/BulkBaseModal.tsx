import {
  Box,
  Button,
  DialogActions,
  DialogContent,
  DialogTitle,
  Table,
  TableBody,
  Typography,
} from '@material-ui/core';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { Dialog } from '../../../../containers/dialogs/Dialog';
import { DialogFooter } from '../../../../containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '../../../../containers/dialogs/DialogTitleWrapper';
import { AllGrievanceTicketQuery } from '../../../../__generated__/graphql';

export const StyledLink = styled.div`
  color: #000;
  text-decoration: underline;
  cursor: pointer;
  display: flex;
  align-content: center;
`;
const StyledTable = styled(Table)`
  min-width: 400px;
  max-width: 800px;
`;
const StyledDialog = styled(Dialog)`
  max-height: 800px;
`;

const Bold = styled.span`
  font-weight: bold;
`;

interface BulkBaseModalProps {
  selectedTickets: AllGrievanceTicketQuery['allGrievanceTicket']['edges'][number]['node'][];
  icon?: React.ReactElement;
  buttonTitle?: string;
  title: string;
  children?: React.ReactNode;
  onSave: (
    tickets: AllGrievanceTicketQuery['allGrievanceTicket']['edges'][number]['node'][],
  ) => void;
}

export const BulkBaseModal = ({
  selectedTickets,
  icon,
  buttonTitle,
  title,
  children,
  onSave,
}: BulkBaseModalProps): React.ReactElement => {
  const [dialogOpen, setDialogOpen] = useState(false);
  const { t } = useTranslation();

  const renderButton = (): React.ReactElement => {
    return (
      <Button
        variant='outlined'
        color='primary'
        startIcon={icon}
        disabled={!selectedTickets.length}
        onClick={() => setDialogOpen(true)}
      >
        {buttonTitle}
      </Button>
    );
  };

  return (
    <>
      {renderButton()}
      <StyledDialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        scroll='paper'
        aria-labelledby='form-dialog-title'
      >
        <DialogTitleWrapper>
          <DialogTitle id='scroll-dialog-title'>{title}</DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <Box mt={2} mb={6}>
            <StyledTable>
              <Typography>
                {t('Tickets ID')}:{' '}
                <Bold>
                  {selectedTickets.map((ticket) => ticket.unicefId).join(', ')}
                </Bold>
              </Typography>
            </StyledTable>
          </Box>
          <StyledTable>
            <TableBody>{children}</TableBody>
          </StyledTable>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button
              onClick={() => {
                setDialogOpen(false);
              }}
            >
              {t('CANCEL')}
            </Button>
            <Button
              variant='contained'
              color='primary'
              onClick={(e) => {
                onSave(selectedTickets);
                setDialogOpen(false);
              }}
            >
              {t('SAVE')}
            </Button>
          </DialogActions>
        </DialogFooter>
      </StyledDialog>
    </>
  );
};
