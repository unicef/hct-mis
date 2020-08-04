import React, { useState } from 'react';
import styled from 'styled-components';
import {
  Button,
  Dialog,
  DialogContent,
  DialogTitle,
  Typography,
} from '@material-ui/core';
import {
  AllProgramsQuery,
  ProgramNode,
  ProgramStatus,
  useUpdateProgramMutation,
} from '../../../__generated__/graphql';
import { PROGRAM_QUERY } from '../../../apollo/queries/Program';
import { ALL_PROGRAMS_QUERY } from '../../../apollo/queries/AllPrograms';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { programCompare } from '../../../utils/utils';
import { useSnackbar } from '../../../hooks/useSnackBar';
import { DialogActions } from '../DialogActions';

const DialogTitleWrapper = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
`;

const DialogFooter = styled.div`
  padding: 12px 16px;
  margin: 0;
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  text-align: right;
`;

const DialogDescription = styled.div`
  margin: 20px 0;
  font-size: 14px;
  color: rgba(0, 0, 0, 0.54);
`;

interface FinishProgramProps {
  program: ProgramNode;
}

export function FinishProgram({
  program,
}: FinishProgramProps): React.ReactElement {
  const [open, setOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const businessArea = useBusinessArea();
  const [mutate] = useUpdateProgramMutation({
    update(cache, { data: { updateProgram } }) {
      cache.writeQuery({
        query: PROGRAM_QUERY,
        variables: {
          id: program.id,
        },
        data: { program: updateProgram.program },
      });
      const allProgramsData: AllProgramsQuery = cache.readQuery({
        query: ALL_PROGRAMS_QUERY,
        variables: { businessArea },
      });
      allProgramsData.allPrograms.edges.sort(programCompare);
      cache.writeQuery({
        query: ALL_PROGRAMS_QUERY,
        variables: { businessArea },
        data: allProgramsData,
      });
    },
  });
  const finishProgram = async (): Promise<void> => {
    const response = await mutate({
      variables: {
        programData: {
          id: program.id,
          status: ProgramStatus.Finished,
        },
      },
    });
    if (!response.errors && response.data.updateProgram) {
      showMessage('Programme finished.', {
        pathname: `/${businessArea}/programs/${response.data.updateProgram.program.id}`,
        dataCy: 'snackbar-program-finish-success',
      });
      setOpen(false);
    } else {
      showMessage('Programme finish action failed.', {
        dataCy: 'snackbar-program-finish-failure',
      });
    }
  };
  return (
    <span>
      <Button
        color='primary'
        onClick={() => setOpen(true)}
        data-cy='button-finish-program'
      >
        Finish Programme
      </Button>
      <Dialog
        open={open}
        onClose={() => setOpen(false)}
        scroll='paper'
        aria-labelledby='form-dialog-title'
      >
        <DialogTitleWrapper>
          <DialogTitle id='scroll-dialog-title'>
            <Typography variant='h6'>Finish Programme</Typography>
          </DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogDescription>
            Are you sure you want to finish this Programme and push data to
            CashAssist?
          </DialogDescription>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setOpen(false)}>CANCEL</Button>
            <Button
              type='submit'
              color='primary'
              variant='contained'
              onClick={finishProgram}
              data-cy='button-finish-program'
            >
              FINISH
            </Button>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </span>
  );
}
