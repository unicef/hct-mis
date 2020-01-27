import React, { useState } from 'react';
import styled from 'styled-components';
import { useHistory } from 'react-router-dom';
import { Button, Dialog, DialogActions, DialogContent, DialogTitle, fade, Typography, } from '@material-ui/core';
import { ProgramNode, useDeleteProgramMutation, } from '../../../__generated__/graphql';
import CloseIcon from '@material-ui/icons/CloseRounded';

const DialogTitleWrapper = styled.div`
  border-bottom: 1px solid #e4e4e4;
`;

const DialogFooter = styled.div`
  padding: 12px 16px;
  margin: 0;
  border-top: 1px solid #e4e4e4;
  text-align: right;
`;

const DialogDescription = styled.div`
  margin: 20px 0;
  font-size: 14px;
  color: rgba(0, 0, 0, 0.54);
`;
const RemoveButton = styled(Button)`
  && {
    color: ${({ theme }) => theme.palette.error.main};
  }
`;

const RemoveModalButton = styled(Button)`
  && {
    background-color: ${({ theme }) => theme.palette.error.main};
  }
  &&:hover {
    background-color: ${({ theme }) => theme.palette.error.dark};
  }
`;

interface DeleteProgramProps {
  program: ProgramNode;
}

export function DeleteProgram({
  program,
}: DeleteProgramProps): React.ReactElement {
  const history = useHistory();
  const [open, setOpen] = useState(false);
  const [mutate] = useDeleteProgramMutation({
    variables: {
      programId: program.id,
    },
  });
  const deleteProgram = async () => {
    await mutate();
    history.push('/programs/');
    setOpen(false);
  };
  return (
    <span>
      <RemoveButton startIcon={<CloseIcon />} onClick={() => setOpen(true)}>
        REMOVE
      </RemoveButton>
      <Dialog
        open={open}
        onClose={() => setOpen(false)}
        scroll='paper'
        aria-labelledby='form-dialog-title'
      >
        <DialogTitleWrapper>
          <DialogTitle id='scroll-dialog-title'>
            <Typography variant='h6'>Remove Programme</Typography>
          </DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogDescription>
            Are you sure you want to remove this Programme?
          </DialogDescription>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setOpen(false)} color='primary'>
              CANCEL
            </Button>
            <RemoveModalButton
              type='submit'
              color='primary'
              variant='contained'
              onClick={deleteProgram}
            >
              REMOVE
            </RemoveModalButton>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </span>
  );
}
