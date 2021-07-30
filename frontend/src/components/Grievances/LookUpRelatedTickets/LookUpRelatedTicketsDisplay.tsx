import { Box, Grid } from '@material-ui/core';
import DeleteIcon from '@material-ui/icons/Delete';
import EditIcon from '@material-ui/icons/Edit';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { RelatedTicketIdDisplay } from './RelatedTicketIdDisplay';

const StyledBox = styled.div`
  border: 1.5px solid #043e91;
  border-radius: 5px;
  font-size: 16px;
  padding: 16px;
  background-color: #f7faff;
`;

const BlueText = styled.span`
  color: #033f91;
  font-weight: 500;
  font-size: 16px;
`;

const LightGrey = styled.span`
  color: #949494;
  margin-right: 10px;
  cursor: pointer;
`;
const DarkGrey = styled.span`
  color: #757575;
  cursor: pointer;
`;

export const LookUpRelatedTicketsDisplay = ({
  values,
  setLookUpDialogOpen,
  onValueChange,
}): React.ReactElement => {
  const { t } = useTranslation();
  const handleRemove = (): void => {
    onValueChange('selectedRelatedTickets', []);
  };
  const renderRelatedTickets = (): React.ReactElement => {
    if (values.selectedRelatedTickets.length) {
      return values.selectedRelatedTickets.map((id) => (
        <RelatedTicketIdDisplay ticketId={id} />
      ));
    }
    return <BlueText>-</BlueText>;
  };
  return (
    <StyledBox>
      <Grid container justify='space-between'>
        <Grid item>
          <Box display='flex' flexDirection='column'>
            {t('Ticket ID')}:{renderRelatedTickets()}
          </Box>
        </Grid>
        <Grid item>
          <Box p={2}>
            <Grid container justify='center' alignItems='center'>
              <Grid item>
                <LightGrey>
                  <EditIcon
                    color='inherit'
                    fontSize='small'
                    onClick={() => setLookUpDialogOpen(true)}
                  />
                </LightGrey>
              </Grid>
              <Grid item>
                <DarkGrey>
                  <DeleteIcon
                    color='inherit'
                    fontSize='small'
                    onClick={() => handleRemove()}
                  />
                </DarkGrey>
              </Grid>
            </Grid>
          </Box>
        </Grid>
      </Grid>
    </StyledBox>
  );
};
